import { writable, derived } from 'svelte/store';

// Maps formId → the Yes/No question shown in the checklist.
// If a conditional form has an entry here, the user must answer before it
// counts toward (or is excluded from) progress.
export const FORM_TRIGGER_QUESTIONS: Record<string, string> = {
  'F-003': 'Will your project drawings bear the seal of a professional engineer?',
  'F-004': 'Is there potential for damage to private or City trees on or near your property?',
  'F-006': 'Are you using the prescriptive energy compliance method under OBC SB-12?',
  'F-007': 'Are you using the performance-based energy compliance method under OBC SB-12?',
  'F-008': 'Is this a residential infill construction project?',
  'F-009': 'Does the project include any plumbing or drain work?',
  'F-011': 'Are you also installing a sump pump as part of this project?',
};

export type ChecklistState = {
  conditions: Record<number, boolean>;
  triggers: Record<string, boolean | null>; // formId → true / false / null (unanswered)
  forms: Record<string, boolean>;
  applied: boolean;
};

export type Bookmark = {
  id: string;
  city: string;
  jobType: string;
  ruleId: string;
  permitName: string;
  label: string;
  savedAt: string;
  rule: unknown;
  fullResult: unknown;
  checklist: ChecklistState;
};

const STORAGE_KEY = 'whatpermit_bookmarks';

function loadFromStorage(): Bookmark[] {
  if (typeof localStorage === 'undefined') return [];
  try {
    const raw: Bookmark[] = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');

    // Fix any ID collisions from bookmarks saved before ruleId was in the API response.
    // Assign each a guaranteed-unique ID while preserving everything else.
    const seen = new Set<string>();
    return raw.map(b => {
      if (seen.has(b.id)) {
        return { ...b, id: `${b.id}-${Math.random().toString(36).slice(2, 7)}` };
      }
      seen.add(b.id);
      return b;
    });
  } catch {
    return [];
  }
}

function initChecklist(rule: unknown): ChecklistState {
  const r = rule as {
    conditions?: string[];
    requiredForms?: { formId: string; mandatory: boolean }[];
  };
  const conditions: Record<number, boolean> = {};
  (r.conditions ?? []).forEach((_, i) => { conditions[i] = false; });

  const triggers: Record<string, boolean | null> = {};
  const forms: Record<string, boolean> = {};
  (r.requiredForms ?? []).forEach(f => {
    forms[f.formId] = false;
    if (!f.mandatory && FORM_TRIGGER_QUESTIONS[f.formId]) {
      triggers[f.formId] = null; // unanswered
    }
  });

  return { conditions, triggers, forms, applied: false };
}

function emptyChecklist(): ChecklistState {
  return { conditions: {}, triggers: {}, forms: {}, applied: false };
}

function createBookmarkStore() {
  const { subscribe, set, update } = writable<Bookmark[]>(loadFromStorage());

  function persist(bookmarks: Bookmark[]) {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(bookmarks));
    }
  }

  return {
    subscribe,

    add(city: string, jobType: string, ruleId: string, permitName: string, rule: unknown, fullResult: unknown) {
      const id = `${city}-${ruleId || 'rule'}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      const bookmark: Bookmark = {
        id, city, jobType, ruleId, permitName,
        label: `${city} – ${permitName}`,
        savedAt: new Date().toISOString(),
        rule, fullResult,
        checklist: initChecklist(rule),
      };
      update(bookmarks => {
        const updated = [bookmark, ...bookmarks];
        persist(updated);
        return updated;
      });
      return id;
    },

    remove(id: string) {
      update(bookmarks => {
        const updated = bookmarks.filter(b => b.id !== id);
        persist(updated);
        return updated;
      });
    },

    isRuleBookmarked(city: string, ruleId: string): boolean {
      let current: Bookmark[] = [];
      const unsub = this.subscribe(v => { current = v; });
      unsub();
      return current.some(b => b.city === city && b.ruleId === ruleId);
    },

    removeByRule(city: string, ruleId: string) {
      update(bookmarks => {
        const updated = bookmarks.filter(b => !(b.city === city && b.ruleId === ruleId));
        persist(updated);
        return updated;
      });
    },

    toggleItem(bookmarkId: string, section: 'conditions' | 'forms' | 'applied', key?: number | string) {
      update(bookmarks => {
        const updated = bookmarks.map(b => {
          if (b.id !== bookmarkId) return b;
          const checklist = { ...emptyChecklist(), ...b.checklist };
          if (section === 'applied') {
            checklist.applied = !checklist.applied;
          } else if (section === 'conditions' && key !== undefined) {
            checklist.conditions = { ...checklist.conditions, [key]: !checklist.conditions[key as number] };
          } else if (section === 'forms' && key !== undefined) {
            checklist.forms = { ...checklist.forms, [key]: !checklist.forms[key as string] };
          }
          return { ...b, checklist };
        });
        persist(updated);
        return updated;
      });
    },

    // Set a trigger question answer (true = yes, false = no)
    setTrigger(bookmarkId: string, formId: string, value: boolean) {
      update(bookmarks => {
        const updated = bookmarks.map(b => {
          if (b.id !== bookmarkId) return b;
          const checklist = { ...emptyChecklist(), ...b.checklist };
          checklist.triggers = { ...checklist.triggers, [formId]: value };
          return { ...b, checklist };
        });
        persist(updated);
        return updated;
      });
    },

    clear() {
      persist([]);
      set([]);
    }
  };
}

export const bookmarks = createBookmarkStore();
export const bookmarkCount = derived(bookmarks, $b => $b.length);

// Progress counts: confirmed conditions + answered trigger questions
// + gathered mandatory forms + gathered triggered-yes forms.
// Does NOT count the "applied" step — that unlocks after 100%.
export function getProgress(bookmark: Bookmark): { done: number; total: number } {
  const rule = bookmark.rule as {
    permitRequired?: boolean;
    conditions?: string[];
    requiredForms?: { formId: string; mandatory: boolean }[];
  };
  const cl: ChecklistState = { ...{ conditions: {}, triggers: {}, forms: {}, applied: false }, ...bookmark.checklist };

  const conditions = rule.conditions ?? [];
  const allForms = rule.requiredForms ?? [];
  const mandatory = allForms.filter(f => f.mandatory);
  const conditionalWithQ = allForms.filter(f => !f.mandatory && FORM_TRIGGER_QUESTIONS[f.formId]);

  const condDone = conditions.filter((_, i) => cl.conditions[i]).length;
  const trigDone = conditionalWithQ.filter(f => cl.triggers[f.formId] !== null && cl.triggers[f.formId] !== undefined).length;
  const mandDone = mandatory.filter(f => cl.forms[f.formId]).length;
  const triggered = conditionalWithQ.filter(f => cl.triggers[f.formId] === true);
  const triggeredDone = triggered.filter(f => cl.forms[f.formId]).length;

  const total = conditions.length + conditionalWithQ.length + mandatory.length + triggered.length;
  const done = condDone + trigDone + mandDone + triggeredDone;

  return { done, total };
}
