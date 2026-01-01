class Post {
  constructor(row) {
    this.id = row.id;
    this.userId = row.user_id;
    this.title = row.title;
    this.content = row.content;
  }
}

module.exports = Post;
