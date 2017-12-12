package sniper

import "github.com/gin-gonic/gin"

func getData(c *gin.Context) { // {{{
	mongo, ok := c.Keys["mongo"].(*MongoDB)
	if !ok {
		c.JSON(400, gin.H{"message": "can't reach db", "body": nil})
	}

	data, err := mongo.GetData()
	// fmt.Printf("\ndata: %v, ok: %v\n", data, ok)
	if err != nil {
		c.JSON(400, gin.H{"message": "can't get data from database", "body": nil})
	} else {
		c.JSON(200, gin.H{"message": "get data sucess", "body": data})
	}
} // }}}

func postData(c *gin.Context) { // {{{
	mongo, ok := c.Keys["mongo"].(*MongoDB)
	if !ok {
		c.JSON(400, gin.H{"message": "can't connect to db", "body": nil})
	}
	var req Data
	err := c.Bind(&req)
	if err != nil {
		c.JSON(400, gin.H{"message": "Incorrect data", "body": nil})
		return
	} else {
		err := mongo.PostData(&req)
		if err != nil {
			c.JSON(400, gin.H{"message": "error post to db", "body": nil})
		}
		c.JSON(200, gin.H{"message": "post data sucess", "body": req})
	}
} 

func main() {
	r := gin.Default()
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "pong",
		})
	})
	r.Run() 
}
