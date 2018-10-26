## About

This repository provides two examples of provisioning a Hyperledger Fabric network.

- the most basic, minimal network possible using a native peer binary and its configuration files, with a native solo orderer binary and its configuration files. It also includes some scripts and their enviroment variables to create, join a channel; install, instantinate chaincode; invoke, query the chaincode. This is in the `./single` directory.
<p align="center">
  <img src="./org0.svg">
</p>

- The second example is much more involved. It uses ansible to create three or more orgs, where each org consists of a zookeeper node, a kafka node, a fabric-ca node, an orderer node, N peer nodes, and a cli node. Each node corresponds to its own virtual machine. It is in the `./ansible` directory.
<p align="center">
  <img src="./orgs.svg">
</p>

These examples assume a basic understanding of what Hyperledger Fabric is, and how the various components interact. The `byfn` example included in Fabric, is a much better first step.
