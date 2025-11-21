<script lang="ts">
import { goto } from '$app/navigation';
import { checkPermit } from '$lib/services/permitService';
let city = "";
let projectType = "";
let address = "";
let postalCode = "";
let loading = false;
let error = '';
async function handleLookup() {
error = '';
loading = true;
try {
const data = await checkPermit({
postal_code: postalCode,
city,
job_type: projectType
});


sessionStorage.setItem('permitResult', JSON.stringify(data));
goto('/lookup');


} catch (err) {
error = 'Could not retrieve permit information. Please try again.';
} finally {
loading = false;
}
}
</script>

<div class="min-h-screen bg-white flex flex-col font-serif">
<div class="flex flex-col items-center justify-center text-center px-6 py-20">
<h1 class="text-4xl md:text-5xl leading-tight max-w-2xl mb-10">
What do you need?<br />
Enter your details and we’ll see what permits you need!
</h1>


<div class="bg-gray-50 border border-gray-200 rounded-xl p-8 w-full max-w-md space-y-5">


{#if error}
<div class="text-red-600 text-sm">{error}</div>
{/if}


<div class="text-left">
<label class="block text-sm font-semibold mb-1">City</label>
<select bind:value={city} class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400">
<option value="">Select city</option>
<option value="Toronto">Toronto</option>
<option value="Mississauga">Mississauga</option>
<option value="Oakville">Oakville</option>
</select>
</div>


<div class="text-left">
<label class="block text-sm font-semibold mb-1">Project Type</label>
<select bind:value={projectType} class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400">
<option value="">What are you building?</option>
<option value="deck">Deck</option>
<option value="basement">Basement Renovation</option>
<option value="fence">Fence</option>
<option value="driveway">Driveway</option>
</select>
</div>


<div class="text-left">
<label class="block text-sm font-semibold mb-1">Postal Code</label>
<input
type="text"
bind:value={postalCode}
placeholder="L5B 3K6"
class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
/>
</div>
<div class="text-left">
<label class="block text-sm font-semibold mb-1">Project Address</label>
<input
type="text"
bind:value={address}
placeholder="123 Main St"
class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
/>
</div>
<button
on:click={handleLookup}
disabled={loading}
class="w-full mt-4 bg-red-600 text-white py-3 rounded-md text-sm font-semibold hover:bg-red-700 transition disabled:opacity-60"
>
{loading ? 'Checking permits...' : 'Look up'}
</button>
</div>
</div>
</div>