module.exports = (sequelize, DataTypes) => {
  const FlashcardDeck = sequelize.define('FlashcardDeck', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    title: {
      type: DataTypes.STRING,
      allowNull: false
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    subject: {
      type: DataTypes.STRING,
      allowNull: true
    },
    course_id: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    user_id: {
      type: DataTypes.STRING,
      allowNull: false
    },
    created_at: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW
    },
    updated_at: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW
    },
    last_studied: {
      type: DataTypes.DATE,
      allowNull: true
    }
  }, {
    tableName: 'flashcard_decks',
    timestamps: true,
    underscored: true
  });

  FlashcardDeck.associate = (models) => {
    FlashcardDeck.hasMany(models.Flashcard, {
      foreignKey: 'deck_id',
      as: 'cards'
    });
  };

  return FlashcardDeck;
};
