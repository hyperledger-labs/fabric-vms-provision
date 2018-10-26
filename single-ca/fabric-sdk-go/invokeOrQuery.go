package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/hyperledger/fabric-sdk-go/pkg/client/channel"
	"github.com/hyperledger/fabric-sdk-go/pkg/client/msp"
	"github.com/hyperledger/fabric-sdk-go/pkg/common/errors/retry"
	mspctx "github.com/hyperledger/fabric-sdk-go/pkg/common/providers/msp"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
)

type FabricSetup struct {
	user       string
	identity   mspctx.SigningIdentity
	configFile string
	channel    string
	chaincode  string
	org        string
	peer       string
	sdk        *fabsdk.FabricSDK
}

func (this *FabricSetup) Init() {
	config := config.FromFile(this.configFile)

	sdk, err := fabsdk.New(config)
	if err != nil {
		log.Printf("failed to create new instance of sdk: %s\n", err)
	}
	this.sdk = sdk

	ctxProvider := this.sdk.Context(fabsdk.WithOrg("org0"))
	mspClient, err := msp.New(ctxProvider)
	if err != nil {
		log.Fatal("failed to create msp client: ", err)
	}

	signingIdentity, err := mspClient.GetSigningIdentity(this.user)
	if err != nil {
		log.Fatal(err)
	}
	this.identity = signingIdentity
}

func (this *FabricSetup) Query(fcn string, args [][]byte) []byte {
	queryReq := channel.Request{
		ChaincodeID: this.chaincode,
		Fcn:         fcn,
		Args:        args,
	}

	clientChannelContext := this.sdk.ChannelContext(this.channel, fabsdk.WithUser(this.user), fabsdk.WithOrg(this.org), fabsdk.WithIdentity(this.identity))
	client, err := channel.New(clientChannelContext)
	if err != nil {
		log.Printf("failed to create a new channel: %s", err)
		return []byte("failed to create new channel")
	}

	res, err := client.Query(queryReq, channel.WithRetry(retry.DefaultChannelOpts), channel.WithTargetEndpoints(this.peer))
	if err != nil {
		log.Printf("failed to query ledger : %s", err)
	}
	return res.Payload
}

func (this *FabricSetup) Invoke(fcn string, args [][]byte) int32 {
	invokeReq := channel.Request{
		ChaincodeID: this.chaincode,
		Fcn:         fcn,
		Args:        args,
	}

	clientChannelContext := this.sdk.ChannelContext(this.channel, fabsdk.WithUser(this.user), fabsdk.WithOrg(this.org), fabsdk.WithIdentity(this.identity))
	client, err := channel.New(clientChannelContext)
	if err != nil {
		log.Printf("failed to create new channel context: %s", err)
		return -1
	}

	res, err := client.Execute(invokeReq, channel.WithRetry(retry.DefaultChannelOpts), channel.WithTargetEndpoints(this.peer))
	if err != nil {
		log.Printf("failed to invoke chaincode: %s\n", err)
		return -1
	}
	log.Printf("%+v\n", res)
	return res.ChaincodeStatus
}

func main() {
	// ./invoke  --config <connection profile yaml>  --action <"invoke" | "query"> --key <"a" | "b">
	flag.Usage = func() {
		fmt.Fprintf(os.Stdout, "Usage:\n")
		fmt.Fprintf(os.Stdout, "%s  --config <connection profile yaml>  --action <invoke | query> --key <a | b>:\n", os.Args[0])
	}
	configFile := flag.String("config", "", "yaml connection profile")
	user := flag.String("user", "", "username")
	action := flag.String("action", "", "invoke or query")
	key := flag.String("key", "", "key to perform action on")

	flag.Parse()

	if *configFile == "" {
		log.Fatal("connection profile required")
	}

	if *action != "invoke" && *action != "query" {
		log.Fatal("action 'invoke' or 'query' required")
	}

	if *key != "b" {
		*key = "a"
	}

	hfc := FabricSetup{
		user:       *user,
		configFile: *configFile,
		channel:    "mychannel",
		chaincode:  "mycc",
		org:        "org0",
		peer:       "peer0.org0.example.com",
	}

	hfc.Init()

	if *action == "query" {
		log.Printf("querying %s\n", *key)
		var q [][]byte
		q = append(q, []byte(*key))
		res := hfc.Query("query", q)
		log.Print(string(res))
	}

	if *action == "invoke" {
		src, dst := "a", "b"
		if src != *key {
			src = "b"
			dst = "a"
		}

		log.Printf("transferring 5 from %s to %s\n", src, dst)
		var i [][]byte
		i = append(i, []byte(src))
		i = append(i, []byte(dst))
		i = append(i, []byte("5"))
		rsp := hfc.Invoke("invoke", i)
		log.Print(rsp)
	}
}
