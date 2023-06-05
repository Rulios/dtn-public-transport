import os

# THIS is a DAEMON to create and orchestrate the DTN nodes

AMOUNT_OF_NODES = 3
BASE_NODE_PORT = 8090
BASE_ENDPOINT = 4556
BASE_AGENT_SERVER_PORT = 6000
MASTER_CLIENT_URL = "localhost:3000"
nodes = []


def startNode(nodeName, nodeLocalIP, nodeEndpoint, nodeAgentPort):
    command = """
    NODE_ID='%s' NODE_LOCAL_IP='%s' NODE_ENDPOINT=':%s' AGENT_PORT='%s'\
    docker compose -p %s up -d
    """ % (
        nodeName,
        nodeLocalIP,
        nodeEndpoint,
        nodeAgentPort,
        nodeName,
    )

    # print(command)

    os.system(command)


def downNode(nodeName):
    command = """
    docker compose -p %s down
    """ % (
        nodeName
    )

    # print(command)
    os.system(command)


print("This daemon controls the startup of containers of each node")

currentNodePort = BASE_NODE_PORT
currentNodeEndpoint = BASE_ENDPOINT
currentNodeAgentPort = BASE_AGENT_SERVER_PORT
for i in range(AMOUNT_OF_NODES):
    nodeName = "node" + str(i)
    nodeLocalIp = "localhost:" + str(currentNodePort)
    nodeEndpoint = currentNodeEndpoint
    nodeAgentPort = currentNodeAgentPort

    print(
        "Starting node (%s) at IP: %s, in the Endpoint: %s"
        % (nodeName, nodeLocalIp, nodeEndpoint)
    )
    print("Agent instanced at 0.0.0.0:%s with the node" % (currentNodeAgentPort))

    startNode(nodeName, nodeLocalIp, nodeEndpoint, nodeAgentPort)

    nodes.append(nodeName)
    currentNodePort += 1
    currentNodeEndpoint += 1
    currentNodeAgentPort += 1


print(nodes)
input("Press any key to take down the nodes")


for node in nodes:
    print("Deleting node (%s)" % (node))
    downNode(node)
    nodes = []
