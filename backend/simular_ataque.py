with open("access.log", "a") as f:
    f.write("45.33.32.156 - - [01/Jul/2026] \"GET /login?user=admin\' OR 1=1-- HTTP/1.1\" 200\n")
print("Linea de ataque anadida")
