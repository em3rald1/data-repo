const discord = require("discord.js");
const client = new discord.Client();

client.on('ready', () => {
    console.log('ready')
})

function depukj() {
    console.log('5555555');
    return;
}

client.on('message', (mes) => {
    if(mes.content == 's!test') {
        mes.channel.send('react message -> read').then((_message) => {
            _message.react("👍").then(() => { 
              _message.react("👎").then(() => {
                
                let i = 0;
                /**
                 * 
                 * @param {discord.MessageReaction} reaction 
                 * @param {discord.User} user 
                 * @returns 
                 */
                const filter = (reaction, user) => {
                    if(reaction.emoji.name == '👍' && user.id == mes.author.id) {
                        _message.edit('read ' + i);
                        i++;
                    }
                }
                let collector = _message.createReactionCollector(filter);
                //collector.on('dispose', filter);
              })
            })
          })
    }
})

client.login('ODE3NzE3NDkxNzg2NDQ4OTA3.YENkwg.DII01PjXlmOsMYI74CLZbuNGY18')