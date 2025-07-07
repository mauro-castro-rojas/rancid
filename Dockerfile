FROM python:3.12-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Apache + CGI + RANCID + ViewVC + build tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      apache2 \
      libapache2-mod-fcgid \
      rancid \
      pkg-config \
      default-libmysqlclient-dev \
      gcc \
      git \
      python3-subversion \
 && rm -rf /var/lib/apt/lists/*

# Fetch and auto-install ViewVC
RUN git clone https://github.com/viewvc/viewvc.git /usr/local/src/viewvc \
 && cd /usr/local/src/viewvc \
 # feed blank lines to accept all defaults in viewvc-install
 && yes '' | ./viewvc-install \
 # make the CGI script available to Apache
 && ln -s /usr/local/src/viewvc/bin/cgi/viewvc.cgi /usr/lib/cgi-bin/viewvc.cgi

# 1) Create a standalone conf to turn on .py CGI under /var/www/html
RUN tee /etc/apache2/conf-available/rancid-python.conf <<"EOF"
<Directory /var/www/html>
    Options +ExecCGI +FollowSymLinks
    AddHandler cgi-script .py
    Require all granted
</Directory>
EOF

# 2) Enable it (and reload modules)
RUN a2enmod cgid fcgid \
 && a2enconf rancid-python


# Mirror original layout and set CWD
WORKDIR /usr/local/rancid
# If building in your /Users/mauro/rancid folder, this copies all your files into the container
COPY . .
# Create symlink so /usr/local/rancid/admin_rancid → /var/www/html/admin_rancid
RUN mkdir -p /var/www/html \
 && ln -s /usr/local/rancid/admin_rancid /var/www/html/admin_rancid \
 && chown -R www-data:www-data /usr/local/rancid

RUN pip install --no-cache-dir -r requirements.txt

RUN { \
      echo "ServerName localhost"; \
    } >> /etc/apache2/apache2.conf

# Expose HTTP port and launch Apache
EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]


