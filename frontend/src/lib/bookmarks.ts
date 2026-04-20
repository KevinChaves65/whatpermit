import { writable, derived } from 'svelte/store';

// Maps "City:formId" → the Yes/No question shown in the checklist.
// Keyed by city so identical form IDs across cities don't collide.
// If a conditional form has an entry here, the user must answer before it
// counts toward (or is excluded from) progress.
export const FORM_TRIGGER_QUESTIONS: Record<string, string> = {
  // Toronto
  'Toronto:F-003': 'Will your project drawings bear the seal of a professional engineer?',
  'Toronto:F-004': 'Is there potential for damage to private or City trees on or near your property?',
  'Toronto:F-006': 'Are you using the prescriptive energy compliance method under OBC SB-12?',
  'Toronto:F-007': 'Are you using the performance-based energy compliance method under OBC SB-12?',
  'Toronto:F-008': 'Is this a residential infill construction project?',
  'Toronto:F-009': 'Does the project include any plumbing or drain work?',
  'Toronto:F-011': 'Are you also installing a sump pump as part of this project?',

  // Mississauga
  'Mississauga:F-009': 'Are engineered roof trusses proposed for this project?',
};

/** Look up the trigger question for a form, scoped to the correct city. */
export function getTriggerQuestion(city: string, formId: string): string | undefined {
  return FORM_TRIGGER_QUESTIONS[`${city}:${formId}`];
}

export type ChecklistState = {
  conditions: Record<number, boolean | null>; // kept for backwards compat, no longer used for progress
  triggers: Record<string, boolean | null>;   // formId → true / false / null (unanswered)
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

function initChecklist(rule: unknown, city: string): ChecklistState {
  const r = rule as {
    conditions?: string[];
    requiredForms?: { formId: string; mandatory: boolean }[];
  };
  const conditions: Record<number, boolean | null> = {};
  (r.conditions ?? []).forEach((_, i) => { conditions[i] = null; });

  const triggers: Record<string, boolean | null> = {};
  const forms: Record<string, boolean> = {};
  (r.requiredForms ?? []).forEach(f => {
    forms[f.formId] = false;
    if (!f.mandatory && getTriggerQuestion(city, f.formId)) {
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
        checklist: initChecklist(rule, city),
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

    updateLabel(id: string, label: string) {
      update(bookmarks => {
        const updated = bookmarks.map(b => b.id === id ? { ...b, label: label.trim() || b.permitName } : b);
        persist(updated);
        return updated;
      });
    },

    toggleItem(bookmarkId: string, section: 'forms' | 'applied', key?: string) {
      update(bookmarks => {
        const updated = bookmarks.map(b => {
          if (b.id !== bookmarkId) return b;
          const checklist = { ...emptyChecklist(), ...b.checklist };
          if (section === 'applied') {
            checklist.applied = !checklist.applied;
          } else if (section === 'forms' && key !== undefined) {
            checklist.forms = { ...checklist.forms, [key]: !checklist.forms[key] };
          }
          return { ...b, checklist };
        });
        persist(updated);
        return updated;
      });
    },

    // Set a condition answer (true = yes, false = no, null = clear)
    setCondition(bookmarkId: string, index: number, value: boolean) {
      update(bookmarks => {
        const updated = bookmarks.map(b => {
          if (b.id !== bookmarkId) return b;
          const checklist = { ...emptyChecklist(), ...b.checklist };
          // clicking the already-active answer deselects it back to null
          const current = checklist.conditions[index];
          checklist.conditions = {
            ...checklist.conditions,
            [index]: current === value ? null : value,
          };
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

  const allForms = rule.requiredForms ?? [];
  const mandatory = allForms.filter(f => f.mandatory);
  const conditionalWithQ = allForms.filter(f => !f.mandatory && getTriggerQuestion(bookmark.city, f.formId));

  // Conditions are informational statements — they don't count toward progress.
  // Progress is: answer all trigger questions + gather all mandatory forms + gather triggered forms.
  const trigDone = conditionalWithQ.filter(f => cl.triggers[f.formId] !== null && cl.triggers[f.formId] !== undefined).length;
  const mandDone = mandatory.filter(f => cl.forms[f.formId]).length;
  const triggered = conditionalWithQ.filter(f => cl.triggers[f.formId] === true);
  const triggeredDone = triggered.filter(f => cl.forms[f.formId]).length;

  const total = conditionalWithQ.length + mandatory.length + triggered.length;
  const done = trigDone + mandDone + triggeredDone;

  return { done, total };
}
