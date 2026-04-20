<script lang="ts">
  import { bookmarkCount } from '$lib/bookmarks';
  export let title = 'What Permit?';
</script>

<header class="flex justify-between items-center px-12 py-6 bg-cream-100 border-b border-cream-300">
  <a href="/" class="text-red-600 font-bold text-lg">{title}</a>
  <nav class="flex items-center space-x-8 text-sm text-ink-900">
    <a href="/" class="hover:text-red-600 transition-colors">Home</a>
    <a href="/lookup" class="hover:text-red-600 transition-colors">Lookup</a>
    <a href="https://kevinchaves.ca" target="_blank" rel="noopener noreferrer" class="hover:text-red-600 transition-colors">Who am I</a>
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
