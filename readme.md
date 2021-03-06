[![Maintainability](https://api.codeclimate.com/v1/badges/25cf8913fbec3dfd4d1e/maintainability)](https://codeclimate.com/github/ZelieM/MT-planting_planner/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/25cf8913fbec3dfd4d1e/test_coverage)](https://codeclimate.com/github/ZelieM/MT-planting_planner/test_coverage)
[![Build Status](https://travis-ci.org/ZelieM/MT-planting_planner.svg?branch=master)](https://travis-ci.org/ZelieM/MT-planting_planner)

# Description

Todo small description of the project and the architecture

## Architecture

Todo use [ASCII flow](http://asciiflow.com/) to draw an architecture schema or include the nice draw

# Installation

### Requirements
- Install [python3](https://www.python.org/)
- Install [PostgreSQL](https://www.postgresql.org)
- (pip should be installed along with python3 but if is not the case, install it as well)
- Install required dependencies with `pip install -r requirements.txt`
- Create  Postgre database named `planting_planner_db`
- Create a Postgre database named `vegetable_library_db`
- Create a Postgre user named `postgres` with password `azerty` and grant him full access to both databases

### Migrations
Execute the migrations on the databases with the following commands:
- `python manage.py migrate`
- `python manage.py migrate --database=db_vegetables_library`

### Secrets
Some secret values are used when running the project.
Those values are not versionned in git and you must create them manually on each machine.
There are located in [planting_planner/settings/secrets/secrets.json](planting_planner/settings/secrets/secrets.json).

Follow those steps to create your secrets:

- Create the file [planting_planner/settings/secrets/secrets.json](planting_planner/settings/secrets/secrets.json)
- Copy the content of [planting_planner/settings/secrets/secrets.json.template](planting_planner/settings/secrets/secrets.json.template)
- Change the values with your secrets

# Development

To develop this project locally, install the requirements (see above).

Then start the project locally with

```
python manage.py runserver
```

## Icons
We use [Fontawesome5](https://fontawesome.com) to insert icons in our HTML templates.
This tool provide nice free [searchable icons](https://fontawesome.com/icons?m=free).

To use an icon, simply insert the following tag and replace `fa-user` by the icon you want

```html
<i class="fas fa-fw fa-user"></i>
```

- `fas` is the *solid* type of icon, Fontawesome provides Solid, Regular, Light and Brand
- `fa-fw` forces the icons to have all the same size

# Tests
To run the unit tests with code coverage, execute

```
coverage run --source='.' manage.py test planner --settings=planting_planner.settings.tests
```

# Production
- Clone the repository
- Ensure that python3 is installed
- Install all requirements (with pip3)
- Install Apache and mod_wsgi
- Migrations: `python3 manage.py migrate --settings=planting_planner.settings.production`
- After each migration, restart apache (`service apache2 restart`)

## Apache configuration
Apache config file (`/etc/apache2/sites-available/lauzeplan.conf`)

````

WSGIPythonPath /home/zmulders/MT-planting_planner

<VirtualHost *:80>
  ServerName lauzeplan.sipr.ucl.ac.be
  Redirect permanent / https://lauzeplan.sipr.ucl.ac.be/
</VirtualHost>


<VirtualHost *:443>
  ServerName lauzeplan.sipr.ucl.ac.be
  DocumentRoot /home/zmulders/MT-planting_planner/planting_planner

  # Specify the path where Apache is authorized to run CGI scripts
  # /webhook/ is the path in the URL
  # the second path is the location of the scripts
  ScriptAlias /webhook/ /home/zmulders/webhook_github_master/

  # Activate CGI for the scripts' folder
  <Directory /home/zmulders/webhook_github_master/>
    Options ExecCGI
    Require all granted
  </Directory>

  # Below is the Django application's configuration
  WSGIScriptAlias / /home/zmulders/MT-planting_planner/planting_planner/wsgi.py
  Alias /static /home/zmulders/MT-planting_planner/planner/static

  <Directory /home/zmulders/MT-planting_planner/planner/static>
    Require all granted
  </Directory>

  <Directory /home/zmulders/MT-planting_planner/planting_planner>
    <Files wsgi.py>
      Require all granted
    </Files>
  </Directory>
  
  SSLCertificateFile /etc/ssl/lauzeplan_sipr_ucl_ac_be.crt
  SSLCertificateKeyFile /etc/ssl/lauzeplan.sipr.ucl.ac.be.key
  SSLCertificateChainFile /etc/ssl/DigiCertCA.crt
</VirtualHost>
````

##Automatic deployment
This project is automatically updated on the server thanks to a CGI script written in Perl.
However, the migrations are not run automatically.


Dump of the vegetable library database, from production server:
 `pg_dump lauzeplan_library -h pgsql.uclouvain.be -p 5440 --username=lauzeplan -f test_dump_db.txt`
 
 
# License
Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)

This is a human-readable summary of (and not a substitute for) the [license](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode).

### You are free to:

Share — copy and redistribute the material in any medium or format
The licensor cannot revoke these freedoms as long as you follow the license terms.

### Under the following terms:

- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

- NonCommercial — You may not use the material for commercial purposes.

- NoDerivatives — If you remix, transform, or build upon the material, you may not distribute the modified material.

- No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.




