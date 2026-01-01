const { Router } = require('express');
const { body } = require('express-validator');
const authController = require('../controllers/authController');
const validators = [
  body('email').isEmail(),
  body('password').isLength({ min: 8 }),
];

const router = Router();

router.post('/login', validators, authController.login);
router.post('/register', validators, authController.register);

module.exports = router;
