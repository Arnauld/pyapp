# Getting started

```
T1> docker-compose up
```

```
T2> docker exec -it devenv /bin/zsh
T2# python3 cli_suppliers.py --host primary --db suppliers --new_db
T2# python3 cli_suppliers.py --host primary --db suppliers --generate --batch_sz 4 --batch_nb 10 --batch_delay 0.5
```


```
lsof -i -sTCP:LISTEN
```
