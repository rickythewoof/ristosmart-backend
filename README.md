TEMP: we are using a postgres container
```bash
docker run --name psql -e POSTGRES_USER=ristosmart -e POSTGRES_DB=ristosmart -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
```