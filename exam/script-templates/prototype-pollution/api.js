const express = require('express')
const bodyParser = require('body-parser');
const inviteCode = 'FakeCodeForInvite';
const app = express()
app.use(bodyParser.text());

const port = 80
const baseUser = { 'picture': 'default.png' }

function createAdmin(user) {
    console.log('CREATED ADMIN')
}

function createUser(user) {
    console.log('CREATED USER')
}

app.get('/', (req, res) => {
    res.send('Let\'s create an admin user in the lab')
})

app.post('/', (req, res) => {
    let user = JSON.parse(req.body);
     if (user.isAdmin && user.inviteCode !== inviteCode) {
        res.send('No invite code? No admin!');
    } else {
        let userToCreate = Object.assign(baseUser, user);
        console.log(userToCreate)
        if (userToCreate.isAdmin) createAdmin(userToCreate);
        else createUser(userToCreate);
        res.send(`Successfully created ${userToCreate.isAdmin ? 'Admin' : 'User'}`)
    }
})

app.listen(port, () => {
    console.log(`Listening on port ${port}`)
})
