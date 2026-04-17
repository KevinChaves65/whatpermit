<script lang="ts">
  import { goto } from '$app/navigation';
  import { checkPermit } from '$lib/services/permitService';

  let city = '';
  let projectType = '';
  let loading = false;
  let error = '';

  async function handleLookup() {
    error = '';

    if (!city || !projectType) {
      error = 'Please select a city and project type.';
      return;
    }

    loading = true;

    try {
      const data = await checkPermit({ city, job_type: projectType });
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
      Enter your details and we'll see what permits you need!
    </h1>

    <div class="bg-gray-50 border border-gray-200 rounded-xl p-8 w-full max-w-md space-y-5">

      {#if error}
        <div class="text-red-600 text-sm">{error}</div>
      {/if}

      <div class="text-left">
        <label for="city" class="block text-sm font-semibold mb-1">City</label>
        <select id="city" bind:value={city} class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400">
          <option value="">Select city</option>
          <option value="Toronto">Toronto</option>
        </select>
      </div>

      <div class="text-left">
        <label for="projectType" class="block text-sm font-semibold mb-1">Project Type</label>
        <select id="projectType" bind:value={projectType} class="w-full p-3 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-400">
          <option value="">What are you building?</option>

          <optgroup label="New Construction">
            <option value="new-building">New Building</option>
            <option value="addition">Home Addition</option>
            <option value="garage">Garage / Carport</option>
            <option value="shed">Shed</option>
            <option value="deck">Deck / Porch</option>
            <option value="temporary-structure">Tent / Canopy (Temporary Structure)</option>
          </optgroup>

          <optgroup label="Renovations & Interior">
            <option value="renovation">Interior Renovation</option>
            <option value="basement">Basement / Second Suite</option>
            <option value="change-of-use">Change of Use</option>
            <option value="cabinetry">Cabinetry / Millwork</option>
            <option value="insulation">Insulation</option>
          </optgroup>

          <optgroup label="Exterior & Structure">
            <option value="retaining-wall">Retaining Wall</option>
            <option value="demolition">Demolition</option>
            <option value="cladding">Cladding / Siding</option>
          </optgroup>

          <optgroup label="Roof & Windows">
            <option value="roof">Roof Replacement</option>
            <option value="skylight">Skylight</option>
            <option value="window-door">Window / Door Replacement</option>
          </optgroup>

          <optgroup label="Mechanical & Plumbing">
            <option value="mechanical-plumbing">HVAC / Plumbing / Furnace</option>
            <option value="backwater-valve">Backwater Valve</option>
            <option value="backflow-prevention">Backflow Prevention</option>
          </optgroup>

          <optgroup label="Energy & Environment">
            <option value="solar">Solar Panels</option>
            <option value="chimney-fireplace">Chimney / Fireplace</option>
            <option value="green-roof">Green Roof</option>
            <option value="wind-turbine">Wind Turbine</option>
          </optgroup>
        </select>
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
