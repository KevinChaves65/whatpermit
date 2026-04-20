<script lang="ts">
  import { goto } from '$app/navigation';
  import { checkPermit, PermitNotFoundError } from '$lib/services/permitService';

  const phrases = [
    'What Permit do you need? Look it up!',
    'Yes! And Bobs your uncle!',
    'Need a Permit? Which one? Look it up!',
    'Checking for a permit? Enter what you need and see!'
  ];

  const phrase = phrases[Math.floor(Math.random() * phrases.length)];

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
      if (err instanceof PermitNotFoundError) {
        error = `No permit data available for "${projectType}" in ${city}. Try a different project type or city.`;
      } else {
        error = 'Could not retrieve permit information. Please try again.';
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen bg-cream-100 flex flex-col font-serif">
  <div class="flex flex-col items-center justify-center text-center px-6 py-20">
    <h1 class="text-4xl md:text-5xl leading-tight max-w-2xl mb-10 text-ink-900">
      {phrase}
    </h1>

    <div class="bg-cream-50 border border-cream-300 rounded-xl p-8 w-full max-w-md space-y-5 shadow-sm">

      {#if error}
        <div class="text-red-600 text-sm">{error}</div>
      {/if}

      <div class="text-left">
        <label for="city" class="block text-sm font-semibold mb-1 text-ink-700">City</label>
        <select id="city" bind:value={city} class="w-full p-3 border border-cream-300 rounded-md text-sm bg-cream-50 text-ink-900 focus:outline-none focus:ring-2 focus:ring-red-400">
          <option value="">Select city</option>
          <option value="Toronto">Toronto</option>
          <option value="Mississauga">Mississauga</option>
        </select>
      </div>

      <div class="text-left">
        <label for="projectType" class="block text-sm font-semibold mb-1 text-ink-700">Project Type</label>
        <select id="projectType" bind:value={projectType} class="w-full p-3 border border-cream-300 rounded-md text-sm bg-cream-50 text-ink-900 focus:outline-none focus:ring-2 focus:ring-red-400">
          <option value="">What are you building?</option>

          <optgroup label="New Construction">
            <option value="new-building">New Building</option>
            <option value="non-residential">Non-Residential Building / Alteration</option>
            <option value="addition">Home Addition</option>
            <option value="garage">Garage / Carport</option>
            <option value="garage-conversion">Garage Conversion</option>
            <option value="shed">Shed</option>
            <option value="deck">Deck / Porch</option>
            <option value="temporary-structure">Tent / Canopy (Temporary Structure)</option>
          </optgroup>

          <optgroup label="Renovations & Interior">
            <option value="renovation">Interior Renovation</option>
            <option value="basement">Basement / Second Suite</option>
            <option value="second-unit">Additional Residential Unit (ARU)</option>
            <option value="basement-entrance">Basement Walkout / Below-Grade Entrance</option>
            <option value="change-of-use">Change of Use</option>
            <option value="cabinetry">Cabinetry / Millwork</option>
            <option value="insulation">Insulation</option>
          </optgroup>

          <optgroup label="Exterior & Structure">
            <option value="retaining-wall">Retaining Wall</option>
            <option value="demolition">Demolition</option>
            <option value="exterior-alteration">Exterior Alterations (Siding / Windows / Roofing)</option>
            <option value="cladding">Cladding / Siding</option>
            <option value="fence">Fence</option>
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
            <option value="fire-safety">Fire Safety Systems</option>
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
