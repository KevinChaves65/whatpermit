export async function checkPermit(payload: {
postal_code: string;
city: string;
job_type: string;
}) {
const response = await fetch('http://localhost:8080/api/permit/check', {
method: 'POST',
headers: {
'Content-Type': 'application/json'
},
body: JSON.stringify(payload)
});


if (!response.ok) {
throw new Error('Failed to retrieve permit data');
}


return response.json();
}