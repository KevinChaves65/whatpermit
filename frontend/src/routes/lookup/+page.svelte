<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { bookmarks } from '$lib/bookmarks';

  type ZoningRules = {
    maxHeightM?: number;
    setbackFrontYardM?: number;
    setbackRearYardM?: number;
    setbackSideYardM?: number;
    lotCoverageMaxPercent?: number;
    minCeilingHeightM?: number;
    notes?: string;
  };

  type Source = {
    authority: string;
    authorityLevel: string;
    section: string;
    bylawReference?: string;
    url: string;
  };

  type Document = {
    name: string;
    url: string;
  };

  type RequiredForm = {
    formId: string;
    name: string;
    url: string;
    mandatory: boolean;
    notes?: string;
  };

  type PermitFee = {
    amount: number | null;
    unit: string;
    effective?: string;
  };

  type PermitRule = {
    ruleId?: string;
    permitRequired: boolean;
    permitName: string;
    description?: string;
    conditions?: string[];
    permitTypes?: string[];
    fee?: PermitFee;
    cost: number;
    costNotes?: string;
    documents?: Document[];
    requiredForms?: RequiredForm[];
    zoningRules?: ZoningRules;
    notes?: string;
    applyOnlineUrl?: string;
    source: Source;
  };

  type Result = {
    city: string;
    jobType: string;
    rules: PermitRule[];
  };

  let result: Result | null = null;
  let error = '';
  // Set of ruleIds that are currently bookmarked
  let bookmarkedRuleIds = new Set<string>();

  onMount(() => {
    const raw = sessionStorage.getItem('permitResult');
    if (!raw) {
      goto('/');
      return;
    }
    try {
      result = JSON.parse(raw);
      if (result) {
        // Sync bookmarked state from store
        let current: import('$lib/bookmarks').Bookmark[] = [];
        const unsub = bookmarks.subscribe(v => { current = v; });
        unsub();
        bookmarkedRuleIds = new Set(
          current
            .filter(b => b.city === result!.city)
            .map(b => b.ruleId)
        );
      }
    } catch {
      error = 'Could not load results. Please try again.';
    }
  });

  function toggleRuleBookmark(rule: PermitRule) {
    if (!result) return;
    if (bookmarkedRuleIds.has(rule.ruleId ?? '')) {
      bookmarks.removeByRule(result.city, rule.ruleId ?? '');
      bookmarkedRuleIds.delete(rule.ruleId ?? '');
      bookmarkedRuleIds = new Set(bookmarkedRuleIds); // trigger reactivity
    } else {
      bookmarks.add(result.city, result.jobType, rule.ruleId ?? '', rule.permitName, rule, result);
      bookmarkedRuleIds.add(rule.ruleId ?? '');
      bookmarkedRuleIds = new Set(bookmarkedRuleIds); // trigger reactivity
    }
  }

  // Separate required vs not-required rules for display
  $: requiredRules = result?.rules.filter(r => r.permitRequired) ?? [];
  $: notRequiredRules = result?.rules.filter(r => !r.permitRequired) ?? [];
</script>

<div class="min-h-screen bg-cream-100 px-6 py-10 flex flex-col items-center font-serif">
  <div class="max-w-3xl w-full">

    <div class="flex items-center justify-between mb-6">
      <button
        on:click={() => goto('/')}
        class="text-sm text-gray-500 hover:text-red-600"
      >
        ← Back to search
      </button>
    </div>

    {#if error}
      <p class="text-red-600">{error}</p>

    {:else if !result}
      <p class="text-gray-500">Loading...</p>

    {:else}
      <h2 class="text-3xl font-serif mb-1 text-ink-900">Permit Results</h2>
      <p class="text-sm text-ink-500 mb-8">
        {result.city} &mdash; {result.jobType}
      </p>

      <!-- PERMIT REQUIRED RULES -->
      {#if requiredRules.length > 0}
        <div class="mb-8">
          <h3 class="text-lg font-semibold text-red-600 mb-4">
            Permit Required ({requiredRules.length} rule{requiredRules.length > 1 ? 's' : ''})
          </h3>

          {#each requiredRules as rule}
            <div class="border border-red-200 rounded-xl p-6 mb-4 bg-cream-50 space-y-4">
              <div class="flex items-start justify-between gap-3">
                <p class="font-semibold text-base">{rule.permitName}</p>
                {#if rule.ruleId}
                  <button
                    on:click={() => toggleRuleBookmark(rule)}
                    class="shrink-0 text-sm px-2.5 py-1 rounded-md border transition
                      {bookmarkedRuleIds.has(rule.ruleId)
                        ? 'bg-red-600 text-white border-red-600 hover:bg-red-700'
                        : 'bg-white text-gray-500 border-gray-300 hover:border-red-400 hover:text-red-600'}"
                    title={bookmarkedRuleIds.has(rule.ruleId) ? 'Remove bookmark' : 'Save this permit'}
                  >
                    {bookmarkedRuleIds.has(rule.ruleId) ? '★ Saved' : '☆ Save'}
                  </button>
                {/if}
              </div>

              {#if rule.description}
                <p class="text-sm text-gray-700">{rule.description}</p>
              {/if}

              {#if rule.conditions && rule.conditions.length > 0}
                <div>
                  <p class="text-sm font-semibold mb-1">Conditions</p>
                  <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {#each rule.conditions as condition}
                      <li>{condition}</li>
                    {/each}
                  </ul>
                </div>
              {/if}

              {#if rule.permitTypes && rule.permitTypes.length > 0}
                <div>
                  <p class="text-sm font-semibold mb-1">Permit Types Needed</p>
                  <div class="flex flex-wrap gap-2">
                    {#each rule.permitTypes as pt}
                      <span class="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">{pt}</span>
                    {/each}
                  </div>
                </div>
              {/if}

              <!-- Required forms -->
              {#if rule.requiredForms && rule.requiredForms.length > 0}
                {@const mandatoryForms = rule.requiredForms.filter(f => f.mandatory)}
                {@const conditionalForms = rule.requiredForms.filter(f => !f.mandatory)}
                <div>
                  <p class="text-sm font-semibold mb-2">Required Forms</p>

                  {#if mandatoryForms.length > 0}
                    <p class="text-xs font-semibold text-red-700 uppercase tracking-wide mb-1">Mandatory</p>
                    <ul class="space-y-2 mb-3">
                      {#each mandatoryForms as form}
                        <li class="flex flex-col gap-0.5">
                          <a
                            href={form.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            class="text-sm font-medium text-red-700 underline hover:text-red-900"
                          >
                            [{form.formId}] {form.name} ↓
                          </a>
                          {#if form.notes}
                            <span class="text-xs text-gray-500">{form.notes}</span>
                          {/if}
                        </li>
                      {/each}
                    </ul>
                  {/if}

                  {#if conditionalForms.length > 0}
                    <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Conditional</p>
                    <ul class="space-y-2">
                      {#each conditionalForms as form}
                        <li class="flex flex-col gap-0.5">
                          <a
                            href={form.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            class="text-sm text-gray-600 underline hover:text-gray-900"
                          >
                            [{form.formId}] {form.name} ↓
                          </a>
                          {#if form.notes}
                            <span class="text-xs text-gray-500">{form.notes}</span>
                          {/if}
                        </li>
                      {/each}
                    </ul>
                  {/if}
                </div>
              {/if}

              <!-- Fee -->
              {#if rule.fee}
                <div class="text-sm">
                  <span class="font-semibold">Fee: </span>
                  {#if rule.fee.amount}
                    ${rule.fee.amount} — {rule.fee.unit}
                  {:else}
                    {rule.fee.unit}
                  {/if}
                </div>
              {/if}

              <!-- Apply online -->
              {#if rule.applyOnlineUrl}
                <a
                  href={rule.applyOnlineUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-block text-sm font-semibold bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition"
                >
                  Apply Online →
                </a>
              {/if}

              <!-- Reference documents -->
              {#if rule.documents && rule.documents.length > 0}
                <div>
                  <p class="text-sm font-semibold mb-1">Application Guides</p>
                  <ul class="space-y-1">
                    {#each rule.documents as doc}
                      <li>
                        <a
                          href={doc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          class="text-sm text-red-600 underline hover:text-red-800"
                        >
                          {doc.name} →
                        </a>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/if}

              {#if rule.notes}
                <p class="text-xs text-gray-500 italic">{rule.notes}</p>
              {/if}

              <div class="pt-2 border-t border-cream-300 text-xs text-ink-500 space-y-1">
                <p><strong>Authority:</strong> {rule.source.authority}</p>
                <p><strong>Reference:</strong> {rule.source.section}</p>
                <a
                  href={rule.source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-red-600 underline"
                >
                  View official source →
                </a>
              </div>
            </div>
          {/each}
        </div>
      {/if}

      <!-- PERMIT NOT REQUIRED RULES -->
      {#if notRequiredRules.length > 0}
        <div>
          <h3 class="text-lg font-semibold text-ink-700 mb-4">
            No Permit Required ({notRequiredRules.length} rule{notRequiredRules.length > 1 ? 's' : ''})
          </h3>

          {#each notRequiredRules as rule}
            <div class="border border-cream-300 rounded-xl p-6 mb-4 bg-cream-50 space-y-4">
              <div class="flex items-start justify-between gap-3">
                <p class="font-semibold text-base">{rule.permitName}</p>
                {#if rule.ruleId}
                  <button
                    on:click={() => toggleRuleBookmark(rule)}
                    class="shrink-0 text-sm px-2.5 py-1 rounded-md border transition
                      {bookmarkedRuleIds.has(rule.ruleId)
                        ? 'bg-red-600 text-white border-red-600 hover:bg-red-700'
                        : 'bg-white text-gray-500 border-gray-300 hover:border-red-400 hover:text-red-600'}"
                    title={bookmarkedRuleIds.has(rule.ruleId) ? 'Remove bookmark' : 'Save this permit'}
                  >
                    {bookmarkedRuleIds.has(rule.ruleId) ? '★ Saved' : '☆ Save'}
                  </button>
                {/if}
              </div>

              {#if rule.description}
                <p class="text-sm text-gray-700">{rule.description}</p>
              {/if}

              {#if rule.conditions && rule.conditions.length > 0}
                <div>
                  <p class="text-sm font-semibold mb-1">Exempt only if all conditions are met</p>
                  <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
                    {#each rule.conditions as condition}
                      <li>{condition}</li>
                    {/each}
                  </ul>
                </div>
              {/if}

              {#if rule.notes}
                <p class="text-xs text-gray-500 italic">{rule.notes}</p>
              {/if}

              <div class="pt-2 border-t border-cream-300 text-xs text-ink-500">
                <p><strong>Authority:</strong> {rule.source.authority}</p>
              </div>
            </div>
          {/each}
        </div>
      {/if}

      <!-- FALLBACK: no rules at all -->
      {#if requiredRules.length === 0 && notRequiredRules.length === 0}
        <p class="text-gray-500">No rules found for this combination. Try a different city or project type.</p>
      {/if}

    {/if}
  </div>
</div>
