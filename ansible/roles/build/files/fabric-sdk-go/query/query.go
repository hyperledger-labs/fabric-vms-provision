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

func main() {
	// ./query  --config <connection profile yaml>  --key <"key">  --org <"org">  --peer <"peer">  --user <username>
	flag.Usage = func() {
		fmt.Fprintf(os.Stdout, "Usage:\n")
		fmt.Fprintf(os.Stdout, "%s  --config <connection profile yaml>  --key <key>  --org <org>  --peer <peer>  --user <username>\n", os.Args[0])
	}
	configFile := flag.String("config", "", "yaml connection profile")
	key := flag.String("key", "", "key to query")
	org := flag.String("org", "", "organisation from connection profile to use")
	peer := flag.String("peer", "", "peer to contact for query")
	user := flag.String("user", "", "username")

	flag.Parse()

	if *configFile == "" {
		log.Fatal("connection profile required")
	}

	if *key == "" {
		log.Fatal("key required")
	}

	if *org == "" {
		log.Fatal("org required")
	}

	if *peer == "" {
		log.Fatal("peer required")
	}

	if *user == "" {
		log.Fatal("user required")
	}

	hfc := FabricSetup{
		user:       *user,
		configFile: *configFile,
		channel:    "mychannel",
		chaincode:  "mycc",
		org:        *org,
		peer:       *peer,
	}

	hfc.Init()

	log.Printf("querying %s in org %s for key %s:\n", *peer, *org, *key)
	var q [][]byte
	q = append(q, []byte(*key))
	res := hfc.Query("query", q)
	log.Print(string(res))
}
