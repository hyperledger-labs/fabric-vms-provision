package main

import (
	"fmt"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	pb "github.com/hyperledger/fabric/protos/peer"
)

type KVChaincode struct{}

func (t *KVChaincode) Init(stub shim.ChaincodeStubInterface) pb.Response {
	fmt.Println("Init")
	return shim.Success(nil)
}

func (t *KVChaincode) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	fmt.Println("Invoke")
	function, args := stub.GetFunctionAndParameters()
	if function == "invoke" {
		return t.invoke(stub, args)
	} else if function == "query" {
		return t.query(stub, args)
	}

	return shim.Error("invalid invoke function name. Expecting \"invoke\" or \"query\"")
}

func (t *KVChaincode) invoke(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	var key string
	var val string
	var err error

	key = args[0]
	val = args[1]

	fmt.Printf("invoke, key:%s value:%s\n", key, val)

	err = stub.PutState(key, []byte(val))
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success(nil)
}

func (t *KVChaincode) query(stub shim.ChaincodeStubInterface, args []string) pb.Response {
	var key string
	var err error

	if len(args) != 1 {
		return shim.Error("incorrect number of arguments. Expecting key to query for")
	}

	key = args[0]
	fmt.Printf("query, key: %s\n", key)

	val, err := stub.GetState(key)
	if err != nil {
		return shim.Error("unable to get value")
	}

	if val == nil {
		return shim.Error("key not found")
	}

	fmt.Printf("query, key/val : %s/%v\n", val)
	return shim.Success(val)
}

func main() {
	err := shim.Start(new(KVChaincode))
	if err != nil {
		fmt.Printf("error starting kv chaincode: %s\n", err)
	}
}
