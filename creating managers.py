import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--surname", required=True)
parser.add_argument("--name", required=True)

parser.add_argument("--age", type=int, default=0, required=True)
parser.add_argument("--adress", required=True)
parser.add_argument("--email", type=int, required=True)
parser.add_argument("--password", required=True)

args = parser.parse_args()

print(requests.post("http://localhost:8080/api/v2/users",
                    json={'surname': args.surname,
                          'name': args.name,
                          'age': args.age,
                          'address': args.address,
                          'email': args.email,
                          'is_manager': 1,
                          'password': args.password}).json())
