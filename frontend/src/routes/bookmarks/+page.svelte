<script lang="ts">
  import { bookmarks, getProgress, getTriggerQuestion } from '$lib/bookmarks';
  import { goto } from '$app/navigation';
  import type { Bookmark } from '$lib/bookmarks';

  type RequiredForm = { formId: string; name: string; url: string; mandatory: boolean; notes?: string };
  type PermitRule = {
    ruleId?: string;
    permitRequired: boolean;
    permitName: string;
    description?: string;
    conditions?: string[];
    permitTypes?: string[];
    fee?: { amount: number | null; unit: string };
    requiredForms?: RequiredForm[];
    notes?: string;
    applyOnlineUrl?: string;
    source?: { authority: string; section: string; url: string };
  };

  function getRule(bookmark: Bookmark): PermitRule | null {
    return (bookmark.rule as PermitRule) ?? null;
  }

  function mandatory(rule: PermitRule) {
    return (rule.requiredForms ?? []).filter(f => f.mandatory);
  }

  function conditionalWithQ(rule: PermitRule, city: string) {
    return (rule.requiredForms ?? []).filter(f => !f.mandatory && getTriggerQuestion(city, f.formId));
  }

  function conditionalWithoutQ(rule: PermitRule, city: string) {
    return (rule.requiredForms ?? []).filter(f => !f.mandatory && !getTriggerQuestion(city, f.formId));
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('en-CA', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  }

  // Per-card editing state: bookmarkId → draft label string
  let editingId: string | null = null;
  let editDraft = '';

  function startEdit(bookmark: Bookmark) {
    editingId = bookmark.id;
    editDraft = bookmark.label || bookmark.permitName;
  }

  function commitEdit(bookmark: Bookmark) {
    bookmarks.updateLabel(bookmark.id, editDraft);
    editingId = null;
  }

  function cancelEdit() {
    editingId = null;
  }

  function focusInput(el: HTMLElement) {
    el.focus();
  }

  // Step numbering — skip step if nothing to show
  function stepNumbers(rule: PermitRule, city: string) {
    const hasTriggerQs = conditionalWithQ(rule, city).length > 0;
    const hasForms = mandatory(rule).length > 0 || (rule.requiredForms ?? []).length > 0;
    let n = 0;
    return {
      step1: hasTriggerQs ? ++n : 0,
      step2: hasForms ? ++n : 0,
      step3: rule.permitRequired ? ++n : 0,
    };
  }
</script>

<div class="min-h-screen bg-cream-100 px-4 sm:px-6 py-8 sm:py-10 flex flex-col items-center font-serif">
  <div class="max-w-3xl w-full">

    <h2 class="text-3xl font-serif mb-1 text-ink-900">My Permit Checklist</h2>
    <p class="text-sm text-ink-500 mb-8">Track your progress gathering documents for each saved permit.</p>

    {#if $bookmarks.length === 0}
      <div class="border border-cream-300 rounded-xl p-10 text-center text-ink-400">
        <p class="text-lg mb-2">No saved permits yet.</p>
        <p class="text-sm mb-6">Search for a permit and click <strong>☆ Save</strong> on the results page.</p>
        <button on:click={() => goto('/')}
          class="text-sm bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition">
          Start a lookup
        </button>
      </div>

    {:else}
      <div class="space-y-6">
        {#each $bookmarks as bookmark (bookmark.id)}
          {@const rule = getRule(bookmark)}
          {@const progress = getProgress(bookmark)}
          {@const gatheringDone = progress.total > 0 && progress.done === progress.total}
          {@const submitted = bookmark.checklist?.applied ?? false}
          {@const pct = progress.total > 0 ? Math.round((progress.done / progress.total) * 100) : 0}

          <div class="border rounded-xl overflow-hidden transition-colors bg-white
            {submitted ? 'border-green-400' : gatheringDone ? 'border-amber-400' : 'border-cream-300'}">

            <!-- ── Card header ── -->
            <div class="px-4 sm:px-6 py-4 flex items-start justify-between gap-4
              {submitted ? 'bg-green-50' : gatheringDone ? 'bg-amber-50' : 'bg-white'}">
              <div class="flex-1 min-w-0">
                <!-- Editable title -->
                <div class="flex items-start gap-2 flex-wrap">
                  {#if editingId === bookmark.id}
                    <input
                      type="text"
                      bind:value={editDraft}
                      on:keydown={e => { if (e.key === 'Enter') commitEdit(bookmark); if (e.key === 'Escape') cancelEdit(); }}
                      on:blur={() => commitEdit(bookmark)}
                      class="flex-1 font-semibold text-base border-b border-ink-300 bg-transparent focus:outline-none focus:border-red-500 text-ink-900"
                      use:focusInput
                    />
                  {:else}
                    <button
                      on:click={() => startEdit(bookmark)}
                      class="font-semibold text-base leading-snug text-left hover:text-red-600 transition-colors group flex items-center gap-1.5"
                      title="Click to rename"
                    >
                      {bookmark.label || bookmark.permitName}
                      <span class="text-ink-300 group-hover:text-red-400 text-xs font-normal transition-colors">✎</span>
                    </button>
                  {/if}
                  {#if submitted}
                    <span class="text-xs font-semibold bg-green-600 text-white px-2 py-0.5 rounded-full">
                      Submitted
                    </span>
                  {:else if gatheringDone}
                    <span class="text-xs font-semibold bg-amber-500 text-white px-2 py-0.5 rounded-full">
                      Ready to apply
                    </span>
                  {/if}
                </div>
                <p class="text-xs text-ink-400 mt-0.5">{bookmark.permitName} &mdash; {bookmark.city} &mdash; saved {formatDate(bookmark.savedAt)}</p>

                <!-- Progress bar -->
                <div class="mt-3">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs text-ink-500">
                      {#if submitted}
                        Application submitted
                      {:else if gatheringDone}
                        All documents gathered — ready to apply
                      {:else}
                        {progress.done} of {progress.total} steps complete
                      {/if}
                    </span>
                    <span class="text-xs font-semibold {gatheringDone ? 'text-amber-600' : 'text-ink-400'}">{pct}%</span>
                  </div>
                  <div class="h-1.5 bg-cream-200 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-300
                      {submitted ? 'bg-green-500' : gatheringDone ? 'bg-amber-500' : 'bg-red-500'}"
                      style="width: {pct}%">
                    </div>
                  </div>
                </div>
              </div>

              <button on:click={() => bookmarks.remove(bookmark.id)}
                class="shrink-0 text-ink-300 hover:text-red-600 transition text-base leading-none mt-0.5"
                aria-label="Remove bookmark">&times;</button>
            </div>

            {#if rule}
              {@const steps = stepNumbers(rule, bookmark.city)}
              <div class="divide-y divide-cream-200">

                <!-- ── Conditions: informational statements only ── -->
                {#if rule.conditions && rule.conditions.length > 0}
                  <div class="px-4 sm:px-6 py-4 bg-cream-50">
                    <p class="text-xs font-semibold uppercase tracking-wide text-ink-400 mb-3">
                      {rule.permitRequired ? 'Conditions' : 'Exemption conditions'}
                    </p>
                    <ul class="space-y-1.5">
                      {#each rule.conditions as condition}
                        <li class="flex items-start gap-2 text-sm text-ink-700">
                          <span class="mt-1.5 shrink-0 w-1.5 h-1.5 rounded-full bg-ink-300"></span>
                          {condition}
                        </li>
                      {/each}
                    </ul>
                  </div>
                {/if}

                <!-- ── Step 1: Trigger questions ── -->
                {#if steps.step1}
                  <div class="px-4 sm:px-6 py-5 space-y-4">
                    <p class="text-xs font-semibold uppercase tracking-wide text-ink-400">
                      Step {steps.step1} — Answer questions
                    </p>

                    <!-- Trigger questions (Yes / No) -->
                    <ul class="space-y-4">
                      {#each conditionalWithQ(rule, bookmark.city) as form}
                        {@const answer = bookmark.checklist?.triggers?.[form.formId] ?? null}
                        <li class="space-y-2">
                          <p class="text-sm text-ink-700">{getTriggerQuestion(bookmark.city, form.formId)}</p>
                          <div class="flex gap-2">
                            <button
                              on:click={() => bookmarks.setTrigger(bookmark.id, form.formId, true)}
                              class="px-4 py-1.5 text-sm rounded-md border font-medium transition
                                {answer === true
                                  ? 'bg-red-600 text-white border-red-600'
                                  : 'bg-white text-ink-700 border-cream-300 hover:border-red-400 hover:text-red-600'}">
                              Yes
                            </button>
                            <button
                              on:click={() => bookmarks.setTrigger(bookmark.id, form.formId, false)}
                              class="px-4 py-1.5 text-sm rounded-md border font-medium transition
                                {answer === false
                                  ? 'bg-ink-900 text-white border-ink-900'
                                  : 'bg-white text-ink-700 border-cream-300 hover:border-ink-400 hover:text-ink-900'}">
                              No
                            </button>
                            {#if answer === false}
                              <span class="self-center text-xs text-ink-400">— form not required</span>
                            {:else if answer === null}
                              <span class="self-center text-xs text-amber-600">← answer to continue</span>
                            {/if}
                          </div>
                        </li>
                      {/each}
                    </ul>
                  </div>
                {/if}

                <!-- ── Step 2: Gather forms ── -->
                {#if steps.step2 && rule.permitRequired}
                  <div class="px-4 sm:px-6 py-5 space-y-4">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-400">
                      Step {steps.step2} — Gather required forms
                    </p>

                    <ul class="space-y-3">
                      <!-- Mandatory forms -->
                      {#if mandatory(rule).length > 0}
                        <li class="text-xs font-semibold text-red-700 uppercase tracking-wide">Mandatory</li>
                        {#each mandatory(rule) as form}
                          {@const checked = bookmark.checklist?.forms?.[form.formId] ?? false}
                          <li class="flex items-start gap-3">
                            <button
                              on:click={() => bookmarks.toggleItem(bookmark.id, 'forms', form.formId)}
                              class="mt-0.5 shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition
                                {checked ? 'bg-red-600 border-red-600 text-white' : 'border-gray-300 hover:border-red-400'}"
                              aria-label="Toggle form">
                              {#if checked}<span class="text-xs leading-none">✓</span>{/if}
                            </button>
                            <div class="flex-1 min-w-0">
                              <a href={form.url} target="_blank" rel="noopener noreferrer"
                                class="text-sm font-medium {checked ? 'text-gray-400 line-through' : 'text-red-700 underline hover:text-red-900'}">
                                [{form.formId}] {form.name} ↓
                              </a>
                              {#if form.notes}<p class="text-xs text-gray-400 mt-0.5">{form.notes}</p>{/if}
                            </div>
                          </li>
                        {/each}
                      {/if}

                      <!-- Conditional forms (with trigger questions) -->
                      {#each conditionalWithQ(rule, bookmark.city) as form}
                        {@const answer = bookmark.checklist?.triggers?.[form.formId] ?? null}
                        {@const checked = bookmark.checklist?.forms?.[form.formId] ?? false}
                        {#if answer === true}
                          <!-- Required based on answer -->
                          <li class="text-xs font-semibold text-red-700 uppercase tracking-wide mt-2">Required for your project</li>
                          <li class="flex items-start gap-3">
                            <button
                              on:click={() => bookmarks.toggleItem(bookmark.id, 'forms', form.formId)}
                              class="mt-0.5 shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition
                                {checked ? 'bg-red-600 border-red-600 text-white' : 'border-gray-300 hover:border-red-400'}"
                              aria-label="Toggle form">
                              {#if checked}<span class="text-xs leading-none">✓</span>{/if}
                            </button>
                            <div class="flex-1 min-w-0">
                              <a href={form.url} target="_blank" rel="noopener noreferrer"
                                class="text-sm font-medium {checked ? 'text-gray-400 line-through' : 'text-red-700 underline hover:text-red-900'}">
                                [{form.formId}] {form.name} ↓
                              </a>
                              {#if form.notes}<p class="text-xs text-gray-400 mt-0.5">{form.notes}</p>{/if}
                            </div>
                          </li>
                        {:else if answer === false}
                          <!-- Skipped -->
                          <li class="flex items-center gap-2 text-sm text-gray-400 italic">
                            <span class="shrink-0 w-5 h-5 rounded border-2 border-gray-200 flex items-center justify-center text-gray-300 text-xs">—</span>
                            [{form.formId}] {form.name} — not required for your project
                          </li>
                        {:else}
                          <!-- Unanswered -->
                          <li class="flex items-center gap-2 text-sm text-gray-400">
                            <span class="shrink-0 w-5 h-5 rounded border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-300 text-xs">?</span>
                            [{form.formId}] {form.name} — answer question in step {steps.step1} first
                          </li>
                        {/if}
                      {/each}

                      <!-- Conditional forms without trigger questions -->
                      {#if conditionalWithoutQ(rule, bookmark.city).length > 0}
                        <li class="text-xs font-semibold text-gray-400 uppercase tracking-wide mt-2">May be required</li>
                        {#each conditionalWithoutQ(rule, bookmark.city) as form}
                          {@const checked = bookmark.checklist?.forms?.[form.formId] ?? false}
                          <li class="flex items-start gap-3">
                            <button
                              on:click={() => bookmarks.toggleItem(bookmark.id, 'forms', form.formId)}
                              class="mt-0.5 shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition
                                {checked ? 'bg-gray-500 border-gray-500 text-white' : 'border-gray-300 hover:border-gray-500'}"
                              aria-label="Toggle form">
                              {#if checked}<span class="text-xs leading-none">✓</span>{/if}
                            </button>
                            <div class="flex-1 min-w-0">
                              <a href={form.url} target="_blank" rel="noopener noreferrer"
                                class="text-sm {checked ? 'text-gray-400 line-through' : 'text-gray-600 underline hover:text-gray-900'}">
                                [{form.formId}] {form.name} ↓
                              </a>
                              {#if form.notes}<p class="text-xs text-gray-400 mt-0.5">{form.notes}</p>{/if}
                            </div>
                          </li>
                        {/each}
                      {/if}
                    </ul>
                  </div>
                {/if}

                <!-- ── Step 3: Submit ── -->
                {#if steps.step3 && rule.permitRequired}
                  <div class="px-4 sm:px-6 py-5">
                    <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-4">
                      Step {steps.step3} — Submit your application
                    </p>

                    {#if submitted}
                      <!-- Submitted state -->
                      <div class="flex items-center gap-3">
                        <span class="shrink-0 w-5 h-5 rounded border-2 bg-green-600 border-green-600 text-white flex items-center justify-center text-xs leading-none">&#10003;</span>
                        <span class="text-sm text-ink-400 line-through">Application submitted</span>
                        <button on:click={() => bookmarks.toggleItem(bookmark.id, 'applied')}
                          class="text-xs text-ink-400 underline hover:text-red-500 ml-auto">Undo</button>
                      </div>

                    {:else if gatheringDone}
                      <!-- Unlocked — ready to apply -->
                      <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-3">
                        <p class="text-sm font-semibold text-amber-800">You've gathered everything — time to apply.</p>
                        {#if rule.applyOnlineUrl}
                          <a href={rule.applyOnlineUrl} target="_blank" rel="noopener noreferrer"
                            class="inline-block text-sm font-semibold bg-red-600 text-white px-5 py-2 rounded-md hover:bg-red-700 transition">
                            Apply Online
                          </a>
                        {:else}
                          <p class="text-xs text-ink-500">Submit your application at your local building office or via email.</p>
                        {/if}
                        <div class="pt-1">
                          <button on:click={() => bookmarks.toggleItem(bookmark.id, 'applied')}
                            class="flex items-center gap-2 text-sm text-ink-700 hover:text-ink-900">
                            <span class="shrink-0 w-5 h-5 rounded border-2 border-cream-300 hover:border-green-500 flex items-center justify-center"></span>
                            Mark as submitted
                          </button>
                        </div>
                      </div>

                    {:else}
                      <!-- Locked -->
                      <div class="flex items-center gap-3 opacity-40 cursor-not-allowed select-none">
                        <span class="shrink-0 w-5 h-5 rounded border-2 border-cream-300 flex items-center justify-center"></span>
                        <div>
                          <p class="text-sm text-ink-700">Apply for your permit</p>
                          <p class="text-xs text-ink-400">Complete steps {steps.step1}{steps.step2 ? ` & ${steps.step2}` : ''} to unlock</p>
                        </div>
                      </div>
                    {/if}
                  </div>
                {/if}

              </div>
            {/if}

          </div>
        {/each}
      </div>

      <button on:click={() => { if (confirm('Remove all saved permits? This cannot be undone.')) bookmarks.clear(); }}
        class="mt-8 text-xs text-ink-400 hover:text-red-500 underline">
        Clear all saved permits
      </button>
    {/if}

  </div>
</div>
