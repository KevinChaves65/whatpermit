<script lang="ts">
  const result = {
    city: "Mississauga",
    projectType: "Deck",
    permitRequired: true,
    permitName: "Residential Deck Permit",
    cost: 250,
    processingTime: "5-10 business days",
    requiredDocuments: [
      "Site Plan",
      "Structural Drawings",
      "Property Survey"
    ],
    inspections: [
      "Footing Inspection",
      "Final Inspection"
    ],
    source: {
      authority: "City of Mississauga",
      section: "Zoning By-law 0225-2007, Section 4.1.3 – Residential Structures",
      url: "https://www.mississauga.ca/services-and-programs/building-and-renovating/building-permits/"
    }
  };
</script>


<div class="min-h-screen bg-white px-6 py-10 flex flex-col items-center">
<div class="max-w-3xl w-full">


<!-- Result Header -->
<h2 class="text-3xl font-serif mb-6">Permit Result</h2>


<!-- Result Card -->
<div class="border border-gray-200 rounded-xl p-8 space-y-5 bg-gray-50">
<div class="flex items-center gap-3">
<span class="text-xl font-semibold">
{result.permitRequired ? '✅ Permit Required' : '❌ No Permit Required'}
</span>
</div>


<div class="space-y-2 text-sm">
<p><strong>City:</strong> {result.city}</p>
<p><strong>Project Type:</strong> {result.projectType}</p>
<p><strong>Permit Name:</strong> {result.permitName}</p>
<p><strong>Estimated Cost:</strong> ${result.cost}</p>
<p><strong>Processing Time:</strong> {result.processingTime}</p>
</div>


<!-- Required Documents -->
<div>
<h3 class="font-semibold mb-2">Required Documents</h3>
<ul class="list-disc list-inside text-sm text-gray-700">
{#each result.requiredDocuments as doc}
<li>{doc}</li>
{/each}
</ul>
</div>


<!-- Inspections -->
<div>
<h3 class="font-semibold mb-2">Required Inspections</h3>
<ul class="list-disc list-inside text-sm text-gray-700">
{#each result.inspections as inspect}
<li>{inspect}</li>
{/each}
</ul>
</div>
</div>


<!-- SOURCE SECTION -->
<div class="mt-8 border-t pt-6 text-sm">
<h4 class="font-semibold mb-2">Source of Information</h4>
<p class="text-gray-700">
Data provided by <strong>{result.source.authority}</strong><br />
<span class="italic">{result.source.section}</span>
</p>
<a
href={result.source.url}
target="_blank"
class="text-red-600 underline text-sm mt-2 inline-block"
>
View official source
</a>
</div>


</div>
</div>