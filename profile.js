const discord = require("discord.js");

/**
 * @param {discord.Message} message 
 * 
 * */

function data(message) {
    message.channel.send("test completed successfully: \nread smth.js").then((_message) => {
        _message.react("👍").then(() => { 
          _message.react("👎").then(() => {
            /**
             * 
             * @param {discord.MessageReaction} reaction 
             * @param {discord.User} user 
             * @returns 
             */
            const filter = (reaction, user) => reaction.emoji.name.includes("thumbs") && user.id == message.author.id;
            _message.awaitReactions(filter, { max: 1 }).then(collected => {
              _message.edit("react read successfully: \nsmth.js > reaction(collected) then")
            })
            .catch(error => {
              _message.edit("react cathed error successfully: \nsmth.js");
            })
          })
        })
      })
}