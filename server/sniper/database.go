package sniper 

import (
	"encoding/base64"
	"fmt"
	rand "math/rand"
	"time"

	"github.com/gin-gonic/gin"

	mgo "gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

type MongoDB struct {
	Host             string
	Port             string
	Addrs            string
	Database         string
	EventTTLAfterEnd time.Duration
	StdEventTTL      time.Duration
	Info             *mgo.DialInfo
	Session          *mgo.Session
}

type Data struct {
	Id   bson.ObjectId `form:"id" bson:"_id,omitempty"`
	Data string        `form:"data" bson:"data"`
}


var letterRunes = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

func rndStr(n int) string {
	rnd_str := make([]rune, n)
	for i := range rnd_str {
		rnd_str[i] = letterRunes[rand.Intn(len(letterRunes))]
	}
	return string(rnd_str)
}

func RandToken(length int) string {
	tbyte := make([]byte, length)
	rand.Read(tbyte)
	return base64.StdEncoding.EncodeToString(tbyte)
}


func (mongo *MongoDB) SetDefault() { // {{{
	mongo.Host = "localhost"
	mongo.Addrs = "localhost:27017"
	mongo.Database = "context"
	mongo.EventTTLAfterEnd = 1 * time.Second
	mongo.StdEventTTL = 20 * time.Minute
	mongo.Info = &mgo.DialInfo{
		Addrs:    []string{mongo.Addrs},
		Timeout:  60 * time.Second,
		Database: mongo.Database,
	}
}

func (mongo *MongoDB) Drop() (err error) { 
	session := mongo.Session.Clone()
	defer session.Close()

	err = session.DB(mongo.Database).DropDatabase()
	if err != nil {
		return err
	}
	return nil
}

func (mongo *MongoDB) Init() (err error) { // {{{
	err = mongo.Drop()
	if err != nil {
		fmt.Printf("\n drop database error: %v\n", err)
	}

	data := Data{}
	data.Data = rndStr(8)
	err = mongo.PostData(&data)

	return err
}

func (mongo *MongoDB) SetSession() (err error) {
	mongo.Session, err = mgo.DialWithInfo(mongo.Info)
	if err != nil {
		mongo.Session, err = mgo.Dial(mongo.Host)
		if err != nil {
			return err
		}
	}
	return err
}

func (mongo *MongoDB) GetData() (dates []Data, err error) { // {{{
	session := mongo.Session.Clone()
	defer session.Close()

	err = session.DB(mongo.Database).C("Data").Find(bson.M{}).All(&dates)
	return dates, err
} // }}}

func (mongo *MongoDB) PostData(data *Data) (err error) { // {{{
	session := mongo.Session.Clone()
	defer session.Close()

	err = session.DB(mongo.Database).C("Data").Insert(&data)
	return err
}

