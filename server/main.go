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
    "io"
    "bytes"

    "github.com/dgrijalva/jwt-go"
    "github.com/gorilla/context"
    "github.com/gorilla/mux"
    "github.com/mitchellh/mapstructure"

    "gopkg.in/mgo.v2"
    "gopkg.in/mgo.v2/bson"

    "crypto/md5"
    // "encoding/hex"
    // "math/rand"

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
    Private bool `json:"priv"`
    Desc string `json:"desc"`
    Code string `json:"code"`
}

type Response struct {
    Success bool `json:"success"`
    Data Snippet `json:"data"`
    Err string `json:"err"`
}

type SignUpResponse struct {
    Success bool `json:"success"`
    Token string `json:"token"`
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
    // router.HandleFunc("/authenticate", CreateTokenEndpoint).Methods("POST")
    router.HandleFunc("/signup", SignUpEndPoint).Methods("POST")
    router.HandleFunc("/signin", SignInEndPoint).Methods("POST")
    router.HandleFunc("/protected", ProtectedEndpoint).Methods("GET")
    router.HandleFunc("/test", ValidateMiddleware(TestEndpoint)).Methods("GET")
    log.Fatal(http.ListenAndServe(":12345", router))
}

func SignUpEndPoint(w http.ResponseWriter, req *http.Request) {

    var user User
    _ = json.NewDecoder(req.Body).Decode(&user)

    u := session.DB("sniper").C("sniper-users")

    var OldUser User
    err := u.Find(bson.M{"user": user.User}).One(&OldUser)
    if err != nil {
        md5Password := md5.New()
        io.WriteString(md5Password, user.Pass)
        buffer := bytes.NewBuffer(nil)
        fmt.Fprintf(buffer, "%x", md5Password.Sum(nil))

        NewPass := buffer.String()

        fmt.Println(NewPass)
        NewUser := User{User: user.User, Pass: NewPass}
        err := u.Insert(&NewUser)
        if err != nil {
            //error inserting user
        } else {
            token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
                "username": user.User,
                "password": NewPass,
            })
            tokenString, error := token.SignedString([]byte("secret"))
            if error != nil {
                fmt.Println(error)
                json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Error Creating User"})
            }
            json.NewEncoder(w).Encode(SignUpResponse{Success: true, Token: tokenString})
        }


    } else {
        json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Username Already Exists"})
    }

}

func SignInEndPoint(w http.ResponseWriter, req *http.Request) {

    var user User
    _ = json.NewDecoder(req.Body).Decode(&user)

    u := session.DB("sniper").C("sniper-users")

    var OldUser User
    err := u.Find(bson.M{"user": user.User}).One(&OldUser)
    if err != nil {
        json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Wrong Credentials"})
    } else {
        md5Password := md5.New()
        io.WriteString(md5Password, user.Pass)
        buffer := bytes.NewBuffer(nil)
        fmt.Fprintf(buffer, "%x", md5Password.Sum(nil))

        NewPass := buffer.String()

        if NewPass == OldUser.Pass {
            token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
                "user": user.User,
                "pass": NewPass,
            })
            tokenString, error := token.SignedString([]byte("secret"))
            if error != nil {
                fmt.Println(error)
                json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Error Creating User"})
            }
            json.NewEncoder(w).Encode(SignUpResponse{Success: true, Token: tokenString})
        } else {
            json.NewEncoder(w).Encode(SignUpResponse{Success: false, Err: "Wrong Credentials"})
        }

    }

}


func PushSnippet(w http.ResponseWriter, req *http.Request) {

    type Data struct {
        Name string `json:"name"`
        User string `json:"user"`
        Private bool `json:"priv"`
        Desc string `json:"desc"`
        Code string `json:"code"`
        Token string `json:"token"`
    }

    var data Data
    _ = json.NewDecoder(req.Body).Decode(&data)

    fmt.Println(data)

    token, _ := jwt.Parse(data.Token, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("There was an error")
        }
        return []byte("secret"), nil
    })

    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        var user User
        mapstructure.Decode(claims, &user)
        fmt.Println(user)

        snippet := Snippet{Name: data.Name, User: user.User, Private: data.Private, Desc: data.Desc, Code: data.Code}

        c := session.DB("sniper").C("sniper-snippets")
        err := c.Insert(&snippet)

        // TODO: Check for duplicate snippits before saving

        if err != nil {
            json.NewEncoder(w).Encode(Response{Success: false, Err: err.Error()})            
            fmt.Println("Error:", err)
        } else {
            json.NewEncoder(w).Encode(Response{Success: true})
            fmt.Println("Snippet saved")
        }
    } else {
        json.NewEncoder(w).Encode(Response{Success: false, Err: "Invalid Authorization Token"})
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

func ProtectedEndpoint(w http.ResponseWriter, req *http.Request) {
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