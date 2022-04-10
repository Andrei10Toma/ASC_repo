### Toma Andrei 331CB

# Tema 1 ASC

## Organizare
### Clasa `Producer`:
Câmpuri:
- products (`List[Tuple[Product, int, float]]`) - lista de tupluri care contin
produsul care va fi publicat secvenţial, cantitatea care va fi publicată din
produsul respectiv şi timpul de aşteptare dupa publicarea sa
- marketplace (`Marketplace`) - referinţă către marketplace
- republish_wait_time - timpul de aşteptare în cazul în care coada
producătorului este plină
- id - identificator numeric unic pentru producător

Metoda `run()` - se parcurge secvenţial lista de produse şi pentru fiecare
produs se încearcă publicarea sa în marketplace.

### Clasa `Consumer`:
Câmpuri:
- carts (`List[List[Dict[str, object]]]`) - conţine acţiunile pe care le va face
un consumator
- marketplace (`Marketplace`) - referinţă către marketplace
- retry_wait_time - timpul aşteptat dacă produsul dorit de consumator nu este
găsit disponibil la niciun producător
- name - numele consumatorului cu care va fi înregistrat cart-ul său.
- cart_id - id-ul cartului pe care consumatorul îl va folosi pentru
cumpărăturile sale

Metoda `run()` - se înregistrează numele consumatorului cu cart_id-ul său se
aplică operaţiile din lista `carts` şi la final după ce au avut loc toate
operaţiile se plasează comanda prin `place_order()`

### Clasa `Marketplace`:
Câmpuri:
- queue_size_per_producer - mărimea cozii pentru fiecare producător
- producer_counter - un contor pentru a ţine cont de numarul de producători
pentru a genera id-ul fiecărui producător
- cart_counter - similar cu `producer_counter` dar pentru cart-uri
- producers_dict (`Dict[int, List[List[Product, int]]]`) - dicţionar de la id-ul
producătorului la o listă de liste care au 2 elemente (primul element este
produsul publicat de producător, iar al doilea reprezintă cart-ul în care se
află produsul). Dacă produsul nu se află în niciun cart atunci valoarea va fi -1
- consumer_cart (`Dict[int, List[Tuple[Product, int]]]`) - dicţionar de la id-ul
cartului la o listă de tupluri de 2 elemente (primul element este produsul care
se află în cart, iar al doilea este id-ul producătorului de la care produsul
este luat)
- cart_consumer_name_dict (`Dict[int, str]`) - dicţionar de la id-ul cartului şi
numele producătorului
- lock (`RLock`) - folosit pentru sincronizare

Metode:
- `add_to_cart()` - se parcurge secvenţial dicţionarul de produse şi în momentul
în care produsul se găseşte la unul dintre producători se face un lock şi se
încearcă adăugarea acestuia în cartul consumerului, altfel se va căuta îm
continuare.
- `remove_from_cart()` - se caută produsul printre produsele din cart, iar când
acesta este găsit se parcurge şi lista producătorului de la care este luat
produsul şi când este găsit şi în lista producătorului se obţine lock-ul şi dacă
produsul este în cart-ul producătorului care trebuie se resetează flag-ul care
are id-ul cartului în care se află produsul şi produsul este eliminat din cart,
fără a fi eliminat din coada producătorului
- `place_order()` - se parcurge lista de produse din cart se caută şi se elimină
pe rând fiecare produs din coada producătorului şi se printează un mesaj. La
final, cartul consumatorului este golit

Tema a fost utilă pentru a înţelege conceptele de sincronizare, dar nu mi s-a
părut neapărat ok implementarea cu sleep, mai bine era folosită implementarea
clasică, cea cu semafoare.

## Implementare
Întregul enunţ al temei este implementat.
Nişte deadlock-uri, dar s-au rezolvat destul de repede.

## Resurse utilizate
- https://ocw.cs.pub.ro/courses/asc/laboratoare/02
- https://ocw.cs.pub.ro/courses/asc/laboratoare/03
- https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler

## Git
- https://github.com/Andrei10Toma/ASC_repo.git
