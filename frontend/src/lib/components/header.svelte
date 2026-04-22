<script lang="ts">
  import { bookmarkCount } from '$lib/bookmarks';
  export let title = 'What Permit?';
</script>

<header class="flex justify-between items-center px-4 sm:px-12 py-4 sm:py-6 bg-cream-100 border-b border-cream-300">
  <a href="/" class="text-red-600 font-bold text-base sm:text-lg shrink-0">{title}</a>
  <nav class="flex items-center gap-3 sm:gap-8 text-sm text-ink-900">
    <a href="/" class="hover:text-red-600 transition-colors hidden sm:inline">Home</a>
    <a href="/lookup" class="hover:text-red-600 transition-colors">Lookup</a>
    <a href="https://kevinchaves.ca" target="_blank" rel="noopener noreferrer" class="hover:text-red-600 transition-colors hidden sm:inline">Who am I</a>
    <a href="/bookmarks" class="hover:text-red-600 transition-colors flex items-center gap-1">
      Saved
      {#if $bookmarkCount > 0}
        <span class="bg-red-600 text-white text-xs font-semibold px-1.5 py-0.5 rounded-full leading-none">
          {$bookmarkCount}
        </span>
      {/if}
    </a>
  </nav>
</header>
