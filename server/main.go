/*
 * Run the server from here bitch.
 *
 * author: HashCode55, exogenesys
 * date  : 13/12/2017
 */

package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/gorilla/mux"
	"github.com/mitchellh/mapstructure"

	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"

	"crypto/md5"
)

type User struct {
	User string `json:"user"`
	Pass string `json:"pass"`
}

type JwtToken struct {
	Token string `json:"token"`
}

type Exception struct {
	Message string `json:"message"`
}

type Snippet struct {
	Name string `json:"name"`
	User string `json:"user"`
	Priv bool   `json:"priv"`
	Desc string `json:"desc"`
	Code string `json:"code"`
	Exec bool   `json:"exec"`
	Time string `json:"time"`
}

type Response struct {
	Success bool      `json:"success"`
	Data    []Snippet `json:"data"`
	Info    string    `json:"info"`
	Err     string    `json:"err"`
}

type SignUpResponse struct {
	Success bool   `json:"success"`
	Token   string `json:"token"`
	Err     string `json:"err"`
}

type Data struct {
	Name  string `json:"name"`
	User  string `json:"user"`
	Priv  bool   `json:"priv"`
	Desc  string `json:"desc"`
	Code  string `json:"code"`
	Token string `json:"token"`
	Exec  bool   `json:"exec"`
	Time  string `json:"time"`
}

func (s *Snippet) String() string {
	return fmt.Sprintf("Name: %v | Desc: %v | Code: %v", s.Name, s.Desc, s.Code)
}

var session *mgo.Session
var debug *bool

func MongoConnect() *mgo.Session {

	// This is a test database which is only for contributors.
	session, err := mgo.Dial("mongodb://snipertest:testsniper@ds125914.mlab.com:25914/sniper")
	if err != nil {
		panic(err)
	} else {
		log.Println("Mon is go")
		// defer session.Close()
	}

	return session
}

func main() {
	// debug flags
	debug = flag.Bool("debug", false, "debug flag")
	// parse the flags
	flag.Parse()
	router := mux.NewRouter()
	session = MongoConnect()
	log.Println("Starting the application...")
	router.HandleFunc("/push", PushSnippet).Methods("POST")
	router.HandleFunc("/pull", PullSnippet).Methods("POST")
	router.HandleFunc("/signup", SignUpEndPoint).Methods("POST")
	router.HandleFunc("/signin", SignInEndPoint).Methods("POST")
	router.HandleFunc("/pushall", PushAllEndPoint).Methods("POST")
	router.HandleFunc("/pullall", PullAllEndPoint).Methods("POST")
	log.Fatal(http.ListenAndServe(":12345", router))
}

func SignUpEndPoint(w http.ResponseWriter, req *http.Request) {

	var user User
	_ = json.NewDecoder(req.Body).Decode(&user)

	log.Println("Received a signup request.")

	u := session.DB("sniper").C("sniper-users")

	var OldUser User
	err := u.Find(bson.M{"user": user.User}).One(&OldUser)
	if err != nil {
		NewPass := HashPassword(user.Pass)
		NewUser := User{User: user.User, Pass: NewPass}
		err := u.Insert(&NewUser)
		if err != nil {
			//error inserting user
			log.Println("Error:", err)
			json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Error saving info."})
		} else {
			tokenString, error := ConstructToken(user.User, NewPass)
			if error != nil {
				json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Error Creating User"})
			} else {
				json.NewEncoder(w).Encode(SignUpResponse{Success: true, Token: tokenString})
			}
		}
	} else {
		json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Username Already Exists"})
	}
}

func SignInEndPoint(w http.ResponseWriter, req *http.Request) {

	var user User
	_ = json.NewDecoder(req.Body).Decode(&user)

	log.Println("Received a signin request.")

	u := session.DB("sniper").C("sniper-users")

	var OldUser User
	err := u.Find(bson.M{"user": user.User}).One(&OldUser)
	if err != nil {
		log.Println("Error:", err)
		json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Wrong Credentials"})
	} else {
		NewPass := HashPassword(user.Pass)
		if NewPass == OldUser.Pass {
			tokenString, error := ConstructToken(user.User, NewPass)
			if error != nil {
				json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Error Creating User"})
			} else {
				json.NewEncoder(w).Encode(SignUpResponse{Success: true, Token: tokenString})
			}
		} else {
			json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Wrong Credentials"})
		}
	}
}

///////////////////////////////
//////    PUSH LOGIC    ///////
///////////////////////////////
func PushSnippet(w http.ResponseWriter, req *http.Request) {

	var data Data
	_ = json.NewDecoder(req.Body).Decode(&data)
	log.Println("Pushing a single snippet...")
	if *debug {
		log.Panicln("[DEBUG] Data: ", data)
	}
	var user User
	//Checks if the JWT is valed
	user, err := DeconstructToken(data.Token)
	// if invalid
	if err != nil {
		//Error in JWT
		log.Println("Invalid authorization token.")
		json.NewEncoder(w).Encode(Response{Success: false, Err: "Invalid authorization token"})
	} else {
		//JWT is valid
		json.NewEncoder(w).Encode(PushSnippetHelper(data, user))
	}
}

func PushAllEndPoint(w http.ResponseWriter, req *http.Request) {
	// data will be received as
	type Anon struct {
		User string `json:"user"`
		Data []struct {
			Name string `json:"NAME"`
			Desc string `json:"DESC"`
			Code string `json:"CODE"`
			Exec bool   `json:"EXEC"`
			Time string `json:"TIME"`
		} `json:"data"`
		Token string `json:"token"`
	}
	log.Println("Pushing all snippets...")
	// get the data from request
	var anon Anon
	_ = json.NewDecoder(req.Body).Decode(&anon)
	// check the token
	var user User
	user, err := DeconstructToken(anon.Token)
	if err != nil {
		//Error in JWT
		log.Println("Invalid authorization token.")
		json.NewEncoder(w).Encode(Response{Success: false, Err: "Invalid Authorization Token"})
	}
	// now loop over snippets and push into the database
	for _, snippet := range anon.Data {
		// by default all snippets will be private
		// ignore the response
		_ = PushSnippetHelper(Data{snippet.Name, anon.User, true,
			snippet.Desc, snippet.Code, anon.Token, snippet.Exec, snippet.Time}, user)
	}
	// send success message
	json.NewEncoder(w).Encode(Response{Success: true, Info: "Successfully pushed all snippets."})
}

func PushSnippetHelper(data Data, user User) Response {
	// this'll be called only if authentication token is valid
	c := session.DB("sniper").C("sniper-snippets")
	//check if there is a snippet for the same name and user
	var oldData Snippet
	err := c.Find(bson.M{"name": data.Name, "user": data.User}).One(&oldData)
	// snippet with same name and user already exists
	if err == nil {
		// just comapare the time
		// time of the received snippet
		receivedTime, err := time.Parse("2006-01-02 15:04:05", data.Time)
		if err != nil {
			log.Println("Error:", err)
		}
		storedTime, err := time.Parse("2006-01-02 15:04:05", oldData.Time)
		if err != nil {
			log.Println("Error:", err)
		}
		if receivedTime.Equal(storedTime) {
			// check if user is trying to make private public or vice a versa
			if (oldData.Priv && !data.Priv) || (!oldData.Priv && data.Priv) {
				// check for public private
				log.Println(oldData.Priv, data.Priv)
				var pubpriv string
				if data.Priv {
					pubpriv = "private."
				} else {
					pubpriv = "public."
				}
				log.Println("Snippet already exists. Making it", pubpriv)

				selector := bson.M{"name": data.Name, "user": data.User}
				change := bson.M{"$set": bson.M{"priv": data.Priv}}
				err = c.Update(selector, change)
				if err != nil {
					return Response{Success: false, Err: "Could not update the snippet."}
					log.Println("Error:", err)
				} else {
					return Response{Success: true, Info: "Snippet has been updated."}
					log.Println("Snippet updated")
				}

				return Response{Success: false, Err: "Made the snippet " + pubpriv}
			}
			log.Println("Snippet already exists.")
			return Response{Success: false, Err: "Snippet already exists."}
		} else {
			// keep the snippet with greater time
			if receivedTime.After(storedTime) {
				selector := bson.M{"name": data.Name, "user": data.User}
				change := bson.M{"$set": bson.M{"code": data.Code, "desc": data.Desc,
					"exec": data.Exec, "time": data.Time}}
				err = c.Update(selector, change)
				if err != nil {
					return Response{Success: false, Err: "Could not update the snippet."}
					log.Println("Error:", err)
				} else {
					return Response{Success: true, Info: "Snippet has been updated."}
					log.Println("Snippet updated")
				}
			} else {
				log.Println("Snippet already exists with updated time.")
				return Response{Success: false, Err: "Snippet already exists."}
			}
		}
	} else {
		// error found, snippet doesnt exist
		snippet := Snippet{Name: data.Name, User: user.User, Priv: data.Priv, Desc: data.Desc,
			Code: data.Code, Exec: data.Exec, Time: data.Time}

		err := c.Insert(&snippet)

		if err != nil {
			return Response{Success: false, Err: err.Error()}
			log.Println("Error:", err)
		} else {
			return Response{Success: true, Info: "Snippet has been saved on the server."}
			log.Println("Snippet saved")
		}
	}
	// control never reaches here
	return Response{}
}

///////////////////////////////
//////    PULL LOGIC    ///////
///////////////////////////////
func PullSnippet(w http.ResponseWriter, req *http.Request) {

	type Data struct {
		Name  string `json:"name"`
		User  string `json:"user"`
		Token string `json:"token"`
	}

	var data Data
	_ = json.NewDecoder(req.Body).Decode(&data)

	log.Println("Pull a snippet.")
	if *debug {
		log.Println("[DEBUG] Data: ", data)
	}

	c := session.DB("sniper").C("sniper-snippets")

	var snippet Snippet
	err := c.Find(bson.M{"name": data.Name, "user": data.User}).One(&snippet)

	if err != nil {
		json.NewEncoder(w).Encode(Response{Success: false, Err: "The requested snippet is either private or not found."})
		log.Println("Error:", err)
	} else {
		if snippet.Priv {
			//Snippet found but is private
			if data.Token != "" {
				//Deconstruct token and match with the corrosponding username
				var user User
				user, err := DeconstructToken(data.Token)
				if err != nil {
					json.NewEncoder(w).Encode(Response{Success: false, Err: "Invalid Authorization Token"})
				} else {
					if user.User == data.User {
						//send private snippet
						json.NewEncoder(w).Encode(Response{Success: true, Data: []Snippet{snippet}})
					}
				}
			} else {
				//Snippet found and authentication token not specified
				json.NewEncoder(w).Encode(Response{Success: false, Err: "The requested snippet is either private or not found."})
			}
		} else {
			//send public snippet
			json.NewEncoder(w).Encode(Response{Success: true, Data: []Snippet{snippet}})
		}
	}
}

func PullAllEndPoint(w http.ResponseWriter, req *http.Request) {

	type Data struct {
		User  string `json:"user"`
		Token string `json:"token"`
	}

	var data Data
	_ = json.NewDecoder(req.Body).Decode(&data)

	c := session.DB("sniper").C("sniper-snippets")

	var snippets []Snippet
	err := c.Find(bson.M{"user": data.User}).All(&snippets)

	if err != nil {
		json.NewEncoder(w).Encode(Response{Success: false, Err: "No snippets found."})
		log.Println("Error:", err)
		//Snippet Not Found
	} else {
		//Check for token
		if data.Token != "" {
			//Deconstruct token and match with the corrosponding username
			var user User
			user, err := DeconstructToken(data.Token)
			log.Println(user)
			if err != nil {
				json.NewEncoder(w).Encode(Response{Success: false, Err: "Invalid Authorization Token."})
			} else {
				if user.User == data.User {
					//send private snippet
					json.NewEncoder(w).Encode(Response{Success: true, Data: snippets})
				}
			}
		} else {
			//Snippet found and authentication token not specified
			json.NewEncoder(w).Encode(Response{Success: false, Err: "Invalid Authorization Token."})
		}
	}

}

///////////////////////////////
////// HELPER FUNCTIONS ///////
///////////////////////////////
func DeconstructToken(JwtToken string) (User, error) {
	token, _ := jwt.Parse(JwtToken, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("There was an error")
		}
		return []byte("secret"), nil
	})
	var user User
	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		mapstructure.Decode(claims, &user)
		return user, nil
	} else {
		return user, fmt.Errorf("Could not deconstruct")
	}
}

func ConstructToken(username string, pass string) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user": username,
		"pass": pass,
	})
	tokenString, error := token.SignedString([]byte("secret"))
	if error != nil {
		log.Println(error)
		return "", error
	} else {
		return tokenString, nil
	}
}

func HashPassword(password string) string {
	md5Password := md5.New()
	io.WriteString(md5Password, password)
	buffer := bytes.NewBuffer(nil)
	fmt.Fprintf(buffer, "%x", md5Password.Sum(nil))
	return buffer.String()
}
