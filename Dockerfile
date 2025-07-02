FROM httpd:2.4

# Copy Angular build to Apache document root
COPY dist/fem-simulation/ /usr/local/apache2/htdocs/

# Copy .htaccess (for SPA routing fallback)
COPY .htaccess /usr/local/apache2/htdocs/