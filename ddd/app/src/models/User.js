class User {
  constructor(row) {
    this.id = row.id;
    this.username = row.username;
    this.email = row.email;
    this.createdAt = row.created_at;
  }
}

module.exports = User;
