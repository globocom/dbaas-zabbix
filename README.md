# dbaas-zabbix
A DBaaS zabbix integration

### Local Deploy

1. Using virtualenv in .virtualenvs/dbaas, execute the following command:

    ``` make fake_deploy ```
    
2. Restart Celery and DBaaS right after that.
    
    
### Prod Deploy

1. Push all of the commits to master.

    ``` git push origin master ```
    
    P.S. Remember to update version in setup.py. e.g. ```setup(...version='0.7.1'->'0.7.2',..```

2. Create new tag with the same version an push to remote repository.
  
    ``` git tag 0.7.2 ```

    ``` git push origin 0.7.2 ```


3. Release

    ```make release ``` (PyPi)

    ```make release_globo ``` (Globo)

    
