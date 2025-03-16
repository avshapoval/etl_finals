db = db.getSiblingDB(process.env.MONGO_INITDB_DB)

db.createUser(
  {
      user: process.env.MONGO_USER,
      pwd: process.env.MONGO_PASSWORD,
      roles: [
          {
              role: "readWrite",
              db:  process.env.MONGO_INITDB_DB
          }
      ]
  }
);

db.createCollection("UserSessions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["session_id", "user_id", "start_time"],
      properties: {
        session_id: { bsonType: "string" },
        user_id: { bsonType: "int" },
        start_time: { bsonType: "date" },
        end_time: { bsonType: "date" },
        pages_visited: {
          bsonType: "array",
          items: { bsonType: "string" }
        },
        device: {
          bsonType: "object",
          properties: {
            type: { bsonType: "string" },
            os: { bsonType: "string" },
            browser: { bsonType: "string" },
            resolution: { bsonType: "string" }
          }
        },
        actions: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              action_type: { bsonType: "string" },
              timestamp: { bsonType: "date" },
              details: { bsonType: "object" }
            }
          }
        }
      }
    }
  }
});

db.createCollection("ProductPriceHistory", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["product_id", "current_price"],
      properties: {
        product_id: { bsonType: "int" },
        price_changes: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["price", "changed_at"],
            properties: {
              price: { bsonType: "decimal" },
              changed_at: { bsonType: "date" }
            }
          }
        },
        current_price: { bsonType: "decimal" },
        currency: { 
          bsonType: "string",
          enum: ["USD", "EUR", "RUB", "CNY"]
        }
      }
    }
  }
});

db.createCollection("EventLogs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["event_id", "timestamp", "event_type"],
      properties: {
        event_id: { bsonType: "string" },
        timestamp: { bsonType: "date" },
        event_type: { 
          bsonType: "string",
          enum: ["user_action", "system", "transaction", "error"]
        },
        details: {
          bsonType: "object",
          properties: {
            source: { bsonType: "string" },
            severity: { bsonType: ["string", "null"] },
            metadata: { bsonType: "object" }
          }
        }
      }
    }
  }
});

db.createCollection("SupportTickets", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["ticket_id", "user_id", "status"],
      properties: {
        ticket_id: { bsonType: "string" },
        user_id: { bsonType: "int" },
        status: {
          bsonType: "string",
          enum: ["open", "in_progress", "closed", "resolved"]
        },
        issue_type: {
          bsonType: "string",
          enum: ["technical", "billing", "general", "refund"]
        },
        messages: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              sender: { 
                bsonType: "string",
                enum: ["user", "support"]
              },
              message: { bsonType: "string" },
              timestamp: { bsonType: "date" }
            }
          }
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("UserRecommendations", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "recommended_products"],
      properties: {
        user_id: { bsonType: "int" },
        recommended_products: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              product_id: { bsonType: "int" },
              score: { bsonType: "double" }
            }
          }
        },
        last_updated: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("ModerationQueue", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["review_id", "user_id", "product_id"],
      properties: {
        review_id: { bsonType: "string" },
        user_id: { bsonType: "int" },
        product_id: { bsonType: "int" },
        review_text: { bsonType: "string" },
        rating: {
          bsonType: "int",
          minimum: 1,
          maximum: 5
        },
        moderation_status: {
          bsonType: "string",
          enum: ["pending", "approved", "rejected"]
        },
        flags: {
          bsonType: "array",
          items: {
            bsonType: "string",
            enum: ["spam", "inappropriate", "fake"]
          }
        },
        submitted_at: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("SearchQueries", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["query_id", "query_text"],
      properties: {
        query_id: { bsonType: "string" },
        user_id: { bsonType: "int" },
        query_text: { bsonType: "string" },
        timestamp: { bsonType: "date" },
        filters: {
          bsonType: "object",
          properties: {
            price_range: {
              bsonType: ["object", "null"],
              properties: {
                min: { bsonType: ["decimal", "null"] },
                max: { bsonType: ["decimal", "null"] }
              }
            },
            category: { bsonType: ["string", "null"] }
          }
        },
        results_count: { bsonType: "int" }
      }
    }
  }
});

print("All collections and indexes created successfully!");