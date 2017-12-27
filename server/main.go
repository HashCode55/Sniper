/*
 * Run the server from here bitch.
 * 
 * author: HashCode55
 * date  : 13/12/2017
*/

package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "strings"
    
    "github.com/dgrijalva/jwt-go"
    "github.com/gorilla/context"
    "github.com/gorilla/mux"
    "github.com/mitchellh/mapstructure"

    "gopkg.in/mgo.v2"
    "gopkg.in/mgo.v2/bson"
)

type User struct {
    Username string `json:"username"`
    Password string `json:"password"`
}

type JwtToken struct {
    Token string `json:"token"`
}

type Exception struct {
    Message string `json:"message"`
}

type Snippet struct {
    Name string `json:"name"`
    Desc string `json:"desc"`
    Code string `json:"code"`
}

type Response struct {
    Success bool `json:"success"`
    Data Snippet `json:"data"`
    Err string `json:"err"`
}

func (s *Snippet) String() string {
    return fmt.Sprintf("Name: %v | Desc: %v | Code: %v", s.Name, s.Desc, s.Code)
}

var session *mgo.Session

func MongoConnect() (*mgo.Session){

    // session, err := mgo.Dial("mongodb://<dbuser>:<dbpassword>@ds231987.mlab.com:31987/sniper")
    session, err := mgo.Dial("mongodb://american-sniper:economyoverecology@ds231987.mlab.com:31987/sniper")
    if err != nil {
        panic(err)
    } else {
        fmt.Println("Mon is go")
        // defer session.Close()
    }

    return session
}


func main() {

    router := mux.NewRouter()
    session = MongoConnect()
    fmt.Println("Starting the application...")
    router.HandleFunc("/push", PushSnippet).Methods("POST")
    router.HandleFunc("/pull", PullSnippet).Methods("GET")
    router.HandleFunc("/authenticate", CreateTokenEndpoint).Methods("POST")
    router.HandleFunc("/protected", ProtectedEndpoint).Methods("GET")
    router.HandleFunc("/test", ValidateMiddleware(TestEndpoint)).Methods("GET")
    log.Fatal(http.ListenAndServe(":12345", router))
}

func CreateTokenEndpoint(w http.ResponseWriter, req *http.Request) {
	/*
	This handler will recieve username and password 
	*/
    var user User
	_ = json.NewDecoder(req.Body).Decode(&user)
	// validate credentials here 	
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
        "username": user.Username,
        "password": user.Password,
    })
    tokenString, error := token.SignedString([]byte("secret"))
    if error != nil {
        fmt.Println(error)
    }
    json.NewEncoder(w).Encode(JwtToken{Token: tokenString})
}

func ProtectedEndpoint(w http.ResponseWriter, req *http.Request) {
	/*
	This is a dummy endpoint. 
	In reality this is where protected snippets are stored 
	OR for storing the snippets 
	*/
    params := req.URL.Query()
    token, _ := jwt.Parse(params["token"][0], func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("There was an error")
        }
        return []byte("secret"), nil
    })
    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        var user User
        mapstructure.Decode(claims, &user)
        json.NewEncoder(w).Encode(user)
    } else {
        json.NewEncoder(w).Encode(Exception{Message: "Invalid authorization token"})
    }
}



func PushSnippet(w http.ResponseWriter, req *http.Request) {

    var snippet Snippet
    _ = json.NewDecoder(req.Body).Decode(&snippet)

    fmt.Println(snippet)

    c := session.DB("sniper").C("sniper-snippets")
    err := c.Insert(&snippet)
    if err != nil {
        json.NewEncoder(w).Encode(Response{Success: false, Err: err.Error()})            
        fmt.Println("Error:", err)
    } else {
        json.NewEncoder(w).Encode(Response{Success: true})
        log.Println("Snippet saved")
    }
}

func PullSnippet(w http.ResponseWriter, req *http.Request) {

    params := req.URL.Query()
    fmt.Println(params["name"][0])

    var snippet Snippet

    c := session.DB("sniper").C("sniper-snippets")

    err := c.Find(bson.M{"name": params["name"][0]}).One(&snippet)
    if err != nil {
        // log.Fatal(err)
        json.NewEncoder(w).Encode(Response{Success: false, Err: err.Error()})
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Snippet:", snippet)
        json.NewEncoder(w).Encode(Response{Success: true, Data: snippet})
    }
}


func ValidateMiddleware(next http.HandlerFunc) http.HandlerFunc {
    return http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
        authorizationHeader := req.Header.Get("authorization")
        if authorizationHeader != "" {
            bearerToken := strings.Split(authorizationHeader, " ")
            if len(bearerToken) == 2 {
                token, error := jwt.Parse(bearerToken[1], func(token *jwt.Token) (interface{}, error) {
                    if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
                        return nil, fmt.Errorf("There was an error")
                    }
                    return []byte("secret"), nil
                })
                if error != nil {
                    json.NewEncoder(w).Encode(Exception{Message: error.Error()})
                    return
                }
                if token.Valid {
                    context.Set(req, "decoded", token.Claims)
                    next(w, req)
                } else {
                    json.NewEncoder(w).Encode(Exception{Message: "Invalid authorization token"})
                }
            }
        } else {
            json.NewEncoder(w).Encode(Exception{Message: "An authorization header is required"})
        }
    })
}

func TestEndpoint(w http.ResponseWriter, req *http.Request) {
    decoded := context.Get(req, "decoded")
    var user User
    mapstructure.Decode(decoded.(jwt.MapClaims), &user)
    json.NewEncoder(w).Encode(user)
}