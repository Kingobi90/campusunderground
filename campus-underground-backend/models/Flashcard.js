module.exports = (sequelize, DataTypes) => {
  const Flashcard = sequelize.define('Flashcard', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    deck_id: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    question: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    answer: {
      type: DataTypes.TEXT,
      allowNull: false
    },
    difficulty: {
      type: DataTypes.INTEGER,
      defaultValue: 0
    },
    next_review: {
      type: DataTypes.DATE,
      allowNull: true
    },
    review_count: {
      type: DataTypes.INTEGER,
      defaultValue: 0
    },
    ai_generated: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    },
    created_at: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW
    },
    updated_at: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW
    }
  }, {
    tableName: 'flashcards',
    timestamps: true,
    underscored: true
  });

  Flashcard.associate = (models) => {
    Flashcard.belongsTo(models.FlashcardDeck, {
      foreignKey: 'deck_id',
      as: 'deck'
    });
    
    Flashcard.hasMany(models.FlashcardFeedback, {
      foreignKey: 'flashcard_id',
      as: 'feedback'
    });
  };

  return Flashcard;
};
