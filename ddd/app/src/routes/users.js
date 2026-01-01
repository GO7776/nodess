const { Router } = require('express');
const userController = require('../controllers/userController');
const auth = require('../middlewares/auth');

const router = Router();

router.get('/me', auth, userController.me);
router.get('/', auth, userController.list);

module.exports = router;
