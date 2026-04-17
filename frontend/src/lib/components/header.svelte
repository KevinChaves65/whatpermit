<script lang="ts">
  import { bookmarkCount } from '$lib/bookmarks';
  export let title = 'What Permit?';
</script>

<header class="flex justify-between items-center px-12 py-6 bg-white border-b">
  <a href="/" class="text-red-600 font-bold text-lg">{title}</a>
  <nav class="flex items-center space-x-8 text-sm text-gray-900">
    <a href="/" class="hover:underline">Home</a>
    <a href="/lookup" class="hover:underline">Lookup</a>
    <a href="/about" class="hover:underline">Who we are</a>
    <a href="/bookmarks" class="hover:underline flex items-center gap-1">
      Saved
      {#if $bookmarkCount > 0}
        <span class="bg-red-600 text-white text-xs font-semibold px-1.5 py-0.5 rounded-full leading-none">
          {$bookmarkCount}
        </span>
      {/if}
    </a>
  </nav>
</header>
