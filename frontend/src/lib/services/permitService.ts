import { PUBLIC_API_URL } from '$env/static/public';

export class PermitNotFoundError extends Error {
  constructor(city: string, jobType: string) {
    super(`No permit data found for "${jobType}" in ${city}.`);
    this.name = 'PermitNotFoundError';
  }
}

export async function checkPermit(payload: {
  city: string;
  job_type: string;
}) {
  const response = await fetch(`${PUBLIC_API_URL}/api/permit/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (response.status === 404) {
    throw new PermitNotFoundError(payload.city, payload.job_type);
  }

  if (!response.ok) {
    throw new Error('Failed to retrieve permit data');
  }

  return response.json();
}
