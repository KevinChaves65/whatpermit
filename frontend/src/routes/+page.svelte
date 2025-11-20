<script lang="ts">
let city = "";
let projectType = "";
let address = "";


function handleLookup() {
console.log({ city, projectType, address });
// Later: connect to Go API
}
</script>


<div class="min-h-screen bg-white flex flex-col font-serif">

<!-- Main Content -->
<main class="flex-1 flex flex-col items-center justify-center text-center px-6">
<h1 class="text-4xl md:text-5xl leading-tight max-w-2xl mb-10">
What do you need?<br />
Enter your details and we’ll see what permits you need!
</h1>


<!-- Form Box -->
<div class="bg-gray-50 border border-gray-200 rounded-xl p-8 w-full max-w-md space-y-5">
<div class="text-left">
<label class="block text-sm font-semibold mb-1">City</label>
<select bind:value={city} class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400">
<option value="">Select city</option>
<option value="Toronto">Toronto</option>
<option value="Mississauga">Mississauga</option>
<option value="Brampton">Brampton</option>
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
bind:value={address}
placeholder="1a1 2b2"
class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
/>
</div>


<button
on:click={handleLookup}
class="w-full mt-4 bg-red-600 text-white py-3 rounded-md text-sm font-semibold hover:bg-red-700 transition"
>
Look up
</button>
</div>
</main>
</div>