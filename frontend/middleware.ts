import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const BACKEND_URL = process.env.API_URL || 'http://backend:8000';

export async function middleware(request: NextRequest) {
  // Only handle API routes
  if (!request.nextUrl.pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  // Get the path and query params
  const path = request.nextUrl.pathname;
  const searchParams = request.nextUrl.searchParams.toString();
  const backendUrl = `${BACKEND_URL}${path}${searchParams ? `?${searchParams}` : ''}`;

  console.log(`[Middleware] Proxying ${request.method} ${backendUrl}`);

  try {
    // Prepare headers
    const headers: Record<string, string> = {};
    request.headers.forEach((value, key) => {
      if (key.toLowerCase() !== 'host') {
        headers[key] = value;
      }
    });

    // Prepare fetch options
    const fetchOptions: RequestInit = {
      method: request.method,
      headers,
      redirect: 'manual', // Handle redirects manually
    };

    // Add body for non-GET requests
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      const contentType = request.headers.get('content-type');
      if (contentType?.includes('multipart/form-data')) {
        // For multipart/form-data, we need to pass the raw body
        // Let the browser/fetch handle the boundary
        const blob = await request.blob();
        fetchOptions.body = blob;
        // Remove content-type header to let fetch set it with the correct boundary
        delete headers['content-type'];
      } else if (contentType?.includes('application/json')) {
        // For JSON, pass the body as-is
        const bodyText = await request.text();
        console.log(`[Middleware] Body: ${bodyText}`);
        if (bodyText) {
          fetchOptions.body = bodyText;
        }
      } else {
        // For other content types
        const bodyText = await request.text();
        if (bodyText) {
          fetchOptions.body = bodyText;
        }
      }
    }

    // Make the request
    const response = await fetch(backendUrl, fetchOptions);

    // Handle redirects - we need to follow them internally instead of sending to client
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get('location');
      if (location && location.includes(BACKEND_URL)) {
        // Follow the redirect internally and return the final response
        console.log(`[Middleware] Following redirect internally: ${location}`);

        const redirectFetchOptions: RequestInit = {
          method: request.method,
          headers,
          redirect: 'manual',
        };

        // If there was a body in the original request, include it in the redirect
        if (fetchOptions.body) {
          redirectFetchOptions.body = fetchOptions.body;
        }

        const redirectResponse = await fetch(location, redirectFetchOptions);

        const redirectBody = await redirectResponse.arrayBuffer();
        const nextResponse = new NextResponse(redirectBody, {
          status: redirectResponse.status,
          statusText: redirectResponse.statusText,
        });

        redirectResponse.headers.forEach((value, key) => {
          nextResponse.headers.set(key, value);
        });

        return nextResponse;
      }
    }

    // Create response with the same body and status
    const responseBody = await response.arrayBuffer();
    const nextResponse = new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
    });

    // Copy headers
    response.headers.forEach((value, key) => {
      nextResponse.headers.set(key, value);
    });

    return nextResponse;
  } catch (error) {
    console.error('[Middleware] Proxy error:', error);
    return NextResponse.json(
      { error: 'Proxy error' },
      { status: 500 }
    );
  }
}

export const config = {
  matcher: '/api/:path*',
};
