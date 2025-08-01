from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.urls import reverse

class AdminAccessMiddleware:
    """
    Middleware to restrict admin access to users who have logged in through the main site.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if this is an admin request
        if request.path.startswith('/admin/'):
            # If user is not authenticated, redirect to main login
            if not request.user.is_authenticated:
                return redirect('/accounts/login/?next=' + request.path)
            
            # If user is authenticated but not staff, show error
            if not (request.user.is_staff or request.user.is_superuser):
                return HttpResponseForbidden(
                    '''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Access Denied - Homelab</title>
                        <style>
                            body {
                                margin: 0;
                                padding: 0;
                                min-height: 100vh;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            }
                            .container {
                                text-align: center;
                                background: rgba(255, 255, 255, 0.1);
                                backdrop-filter: blur(10px);
                                border-radius: 20px;
                                padding: 3rem 2rem;
                                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                                border: 1px solid rgba(255, 255, 255, 0.2);
                                max-width: 500px;
                                width: 90%;
                            }
                            h1 {
                                color: white;
                                font-size: 2.5rem;
                                margin-bottom: 1rem;
                                font-weight: 300;
                                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                            }
                            p {
                                color: rgba(255, 255, 255, 0.9);
                                font-size: 1.1rem;
                                line-height: 1.6;
                                margin-bottom: 1.5rem;
                            }
                            .buttons {
                                display: flex;
                                gap: 1rem;
                                justify-content: center;
                                flex-wrap: wrap;
                                margin-top: 2rem;
                            }
                            a {
                                display: inline-block;
                                padding: 12px 24px;
                                background: rgba(255, 255, 255, 0.2);
                                color: white;
                                text-decoration: none;
                                border-radius: 25px;
                                border: 1px solid rgba(255, 255, 255, 0.3);
                                transition: all 0.3s ease;
                                font-weight: 500;
                            }
                            a:hover {
                                background: rgba(255, 255, 255, 0.3);
                                transform: translateY(-2px);
                                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                            }
                            .icon {
                                font-size: 4rem;
                                margin-bottom: 1rem;
                                opacity: 0.8;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="icon">🔒</div>
                            <h1>Access Denied</h1>
                            <p>You must be a staff member to access the admin panel.</p>
                            <p>Please contact an administrator if you need access.</p>
                            <div class="buttons">
                                <a href="/accounts/login/">Login</a>
                                <a href="/">Go to Main Site</a>
                            </div>
                        </div>
                    </body>
                    </html>
                    '''
                )
            
            # Mark that user accessed admin through main site
            request.session['admin_access_granted'] = True

        response = self.get_response(request)
        return response
