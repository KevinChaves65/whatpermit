<script lang="ts">
	import { onMount } from 'svelte';
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import Header from '$lib/components/header.svelte';
	import Footer from '$lib/components/footer.svelte';
	import { PUBLIC_API_URL } from '$env/static/public';

	let { children } = $props();

	onMount(() => {
		fetch(`${PUBLIC_API_URL}/health`).catch(() => {});
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="min-h-screen flex flex-col font-serif bg-white">
<Header />


<main class="flex-1">
<slot />
</main>


<Footer />
</div>