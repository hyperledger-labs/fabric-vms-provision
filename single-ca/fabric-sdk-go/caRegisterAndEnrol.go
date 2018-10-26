package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/hyperledger/fabric-sdk-go/pkg/client/msp"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/fabsdk"
)

func main() {
	// ./invoke  --config <connection profile yaml>  --user <username>  --pass <password>
	flag.Usage = func() {
		fmt.Fprintf(os.Stdout, "Usage:\n")
		fmt.Fprintf(os.Stdout, "%s  --config <connection profile yaml>  --user <username>  --pass <password>\n", os.Args[0])
	}
	configFile := flag.String("config", "", "yaml connection profile")
	username := flag.String("user", "", "username")
	password := flag.String("pass", "", "password")

	flag.Parse()

	if *configFile == "" {
		log.Fatal("connection profile required")
	}

	config := config.FromFile(*configFile)

	sdk, err := fabsdk.New(config)
	if err != nil {
		log.Printf("failed to create sdk: %s\n", err)
	}

	ctxProvider := sdk.Context(fabsdk.WithOrg("org0"))
	mspClient, err := msp.New(ctxProvider)
	if err != nil {
		log.Fatal("failed to create msp client: ", err)
	}

	signingIdentity, err := mspClient.GetSigningIdentity(*username)
	if err != nil {
		log.Printf("check if user %s is enrolled: %s\n", *username, err.Error())

		identity, err := mspClient.GetIdentity(*username)
		if err != nil {
			log.Printf("user %s does not exist, registering\n", *username)
			// if Secret not given, it is auto generated and returned
			s, err := mspClient.Register(&msp.RegistrationRequest{Name: *username, Secret: *password})
			if err != nil {
				log.Fatal("registration failed: ", err)
			}
			log.Println(s)
		} else {
			log.Printf("identity: %s\n", identity.Secret)
		}

		err = mspClient.Enroll(*username, msp.WithSecret(*password))
		if err != nil {
			log.Fatalf("enroll %s failed: %v\n", *username, err)
		}

		// try getting signingIdentity again
		signingIdentity, err = mspClient.GetSigningIdentity(*username)
		if err != nil {
			log.Fatal(err)
		}
	}
	log.Printf("%s, %s: %s\n", signingIdentity.Identifier().ID, signingIdentity.Identifier().MSPID, string(signingIdentity.EnrollmentCertificate()[:]))
}
