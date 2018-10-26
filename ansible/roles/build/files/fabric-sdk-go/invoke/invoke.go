package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/google/uuid"
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

func (this *FabricSetup) Invoke(fcn string, duration int) {
	clientChannelContext := this.sdk.ChannelContext(this.channel, fabsdk.WithUser(this.user), fabsdk.WithOrg(this.org), fabsdk.WithIdentity(this.identity))
	client, err := channel.New(clientChannelContext)
	if err != nil {
		log.Printf("failed to create new channel context: %s", err)
		return
	}

	count := 0
	lEnd := time.Duration(duration) * time.Second
	for lStart := time.Now(); time.Since(lStart) < lEnd; count++ {
		key := uuid.New().String()
		val := time.Now().Format(time.RFC3339)

		var args [][]byte
		args = append(args, []byte(key))
		args = append(args, []byte(val))

		log.Printf("%8d store (key/value): (%s / %s)\n", count, key, val)
		invokeReq := channel.Request{
			ChaincodeID: this.chaincode,
			Fcn:         fcn,
			Args:        args,
		}

		res, err := client.Execute(invokeReq, channel.WithRetry(retry.DefaultChannelOpts), channel.WithTargetEndpoints(this.peer))
		if err != nil {
			log.Printf("failed to invoke chaincode: %s\n", err)
			continue
		}
		log.Printf("%8d response: %d\n", count, res.ChaincodeStatus)
	}
}

func main() {
	// ./invoke  --config <connection profile yaml>  --duration <"seconds (default=10)">  --org <"org">  --peer <"peer">  --user <"username">
	flag.Usage = func() {
		fmt.Fprintf(os.Stdout, "Usage:\n")
		fmt.Fprintf(os.Stdout, "%s  --config <connection profile yaml>  --duration <seconds (default=10)>  --org <org>  --peer <peer>  --user <username>\n", os.Args[0])
	}
	configFile := flag.String("config", "", "yaml connection profile")
	duration := flag.Int("duration", 10, "duration in seconds to send transactions")
	org := flag.String("org", "", "organisation from connection profile to use")
	peer := flag.String("peer", "", "peer to contact for query")
	user := flag.String("user", "", "username")

	flag.Parse()

	if *configFile == "" {
		log.Fatal("connection profile required")
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

	hfc.Invoke("invoke", *duration)
}
