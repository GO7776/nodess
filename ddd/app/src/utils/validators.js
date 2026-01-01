const { body } = require('express-validator');

exports.registerRules = [
  body('username').isLength({ min: 3 }),
  body('email').isEmail(),
  body('password').isLength({ min: 8 }),
];
