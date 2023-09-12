# IEP_Projekat_2022

Ako je potrebno da se obrišu keširani kontejneri:
```
docker system prune
```

## Pokretanje:

- Potrebno je napraviti image authentication i authenticationDBMigration preko dockerfile-a:
```
docker build -t customer -f customer.dockerfile .
docker build -t daemon -f daemon.dockerfile .
docker build -t storeadmin -f storeAdmin.dockerfile .
docker build -t warehouse -f warehouse.dockerfile .
docker build -t storedbmigration -f storeDBMigration.dockerfile .
docker build -t authentication -f authentication.dockerfile .
docker build -t authenticationdbmigration -f authenticationDBMigration.dockerfile .


docker-compose -f deployement.yaml up
```
<br/>

- Za upravljanje bazom može se koristiti `adminer`
```
username: root
password: root
server: authenticationDB
```
<br/>

- Testovi se pokreću sledećom komandom:
```
python3 main.py --authentication-address http://127.0.0.1:5002 --jwt-secret JWT_SECRET_KEY --roles-field roles --customer-role kupac --warehouse-role magacioner --administrator-role admin --with-authentication --type authentication
```
