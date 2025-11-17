import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const BACKEND_URL = process.env.API_URL || 'http://backend:8000';

export async function proxy(request: NextRequest) {
  if (!request.nextUrl.pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  const path = request.nextUrl.pathname;
  const searchParams = request.nextUrl.searchParams.toString();
  const backendUrl = `${BACKEND_URL}${path}${searchParams ? `?${searchParams}` : ''}`;

  console.log(`[Proxy] ${request.method} ${backendUrl}`);

  try {
    const headers: Record<string, string> = {};
    request.headers.forEach((value, key) => {
      if (key.toLowerCase() !== 'host') {
        headers[key] = value;
      }
    });

    const fetchOptions: RequestInit = {
      method: request.method,
      headers,
      redirect: 'manual',
    };

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      const contentType = request.headers.get('content-type');
      if (contentType?.includes('multipart/form-data')) {
        const blob = await request.blob();
        fetchOptions.body = blob;
        delete headers['content-type'];
      } else {
        const bodyText = await request.text();
        if (bodyText) {
          fetchOptions.body = bodyText;
        }
      }
    }

    const response = await fetch(backendUrl, fetchOptions);

    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get('location');
      if (location && location.includes(BACKEND_URL)) {
        console.log(`[Proxy] following redirect ${location}`);
        const redirectResponse = await fetch(location, fetchOptions);
        const redirectBody = await redirectResponse.arrayBuffer();
        const redirectNextResponse = new NextResponse(redirectBody, {
          status: redirectResponse.status,
          statusText: redirectResponse.statusText,
        });
        redirectResponse.headers.forEach((value, key) => {
          redirectNextResponse.headers.set(key, value);
        });
        return redirectNextResponse;
      }
    }

    const responseBody = await response.arrayBuffer();
    const nextResponse = new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
    });

    response.headers.forEach((value, key) => {
      nextResponse.headers.set(key, value);
    });

    return nextResponse;
  } catch (error) {
    console.error('[Proxy] error:', error);
    return NextResponse.json({ error: 'Proxy error' }, { status: 500 });
  }
}

export const config = {
  matcher: '/api/:path*',
};
