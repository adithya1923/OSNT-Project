from nest.topology import Node, connect


def main():
    h1 = Node("h1")
    h2 = Node("h2")

    h1_if, h2_if = connect(h1, h2)

    h1_if.set_address("10.0.0.1/24")
    h2_if.set_address("10.0.0.2/24")

    print("Ping result:", h1.ping(h2_if.address))


if __name__ == "__main__":
    main()