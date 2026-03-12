import { useEffect, useState } from 'react';

const FALLBACK_LOGO = '/logo.png';

let cachedLogo: string | null = null;
let logoRequest: Promise<string> | null = null;

async function fetchPortalLogo(): Promise<string> {
  if (cachedLogo) return cachedLogo;
  if (!logoRequest) {
    logoRequest = fetch('/api/v2/admin/logo')
      .then(async (res) => {
        if (!res.ok) return FALLBACK_LOGO;
        const data = await res.json().catch(() => ({}));
        return typeof data?.logo === 'string' && data.logo.trim() ? data.logo : FALLBACK_LOGO;
      })
      .catch(() => FALLBACK_LOGO)
      .then((logo) => {
        cachedLogo = logo;
        return logo;
      });
  }
  return logoRequest;
}

export function usePortalLogo(): string {
  const [logo, setLogo] = useState<string>(cachedLogo || FALLBACK_LOGO);

  useEffect(() => {
    let isMounted = true;
    fetchPortalLogo().then((value) => {
      if (isMounted) setLogo(value);
    });
    return () => {
      isMounted = false;
    };
  }, []);

  return logo;
}
