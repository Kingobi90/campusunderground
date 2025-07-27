module.exports = (sequelize, DataTypes) => {
  const FlashcardFeedback = sequelize.define('FlashcardFeedback', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    flashcard_id: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    user_id: {
      type: DataTypes.STRING,
      allowNull: false
    },
    feedback_text: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    rating: {
      type: DataTypes.ENUM('helpful', 'not_helpful', 'needs_improvement'),
      allowNull: true
    },
    created_at: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW
    }
  }, {
    tableName: 'flashcard_feedback',
    timestamps: true,
    underscored: true
  });

  FlashcardFeedback.associate = (models) => {
    FlashcardFeedback.belongsTo(models.Flashcard, {
      foreignKey: 'flashcard_id',
      as: 'flashcard'
    });
  };

  return FlashcardFeedback;
};
