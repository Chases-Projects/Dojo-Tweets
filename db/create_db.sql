-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema dojo_tweets_db
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `dojo_tweets_db` ;

-- -----------------------------------------------------
-- Schema dojo_tweets_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `dojo_tweets_db` DEFAULT CHARACTER SET utf8 ;
USE `dojo_tweets_db` ;

-- -----------------------------------------------------
-- Table `dojo_tweets_db`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dojo_tweets_db`.`users` ;

CREATE TABLE IF NOT EXISTS `dojo_tweets_db`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL,
  `last_name` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dojo_tweets_db`.`tweets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dojo_tweets_db`.`tweets` ;

CREATE TABLE IF NOT EXISTS `dojo_tweets_db`.`tweets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `content` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_tweets_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_tweets_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `dojo_tweets_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dojo_tweets_db`.`likes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dojo_tweets_db`.`likes` ;

CREATE TABLE IF NOT EXISTS `dojo_tweets_db`.`likes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `user_id` INT NOT NULL,
  `tweet_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_likes_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_likes_tweets1_idx` (`tweet_id` ASC) VISIBLE,
  CONSTRAINT `fk_likes_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `dojo_tweets_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_likes_tweets1`
    FOREIGN KEY (`tweet_id`)
    REFERENCES `dojo_tweets_db`.`tweets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dojo_tweets_db`.`follows`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dojo_tweets_db`.`follows` ;

CREATE TABLE IF NOT EXISTS `dojo_tweets_db`.`follows` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  `user_following` INT NOT NULL,
  `user_followed` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_follows_users1_idx` (`user_following` ASC) VISIBLE,
  INDEX `fk_follows_users2_idx` (`user_followed` ASC) VISIBLE,
  CONSTRAINT `fk_follows_users1`
    FOREIGN KEY (`user_following`)
    REFERENCES `dojo_tweets_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_follows_users2`
    FOREIGN KEY (`user_followed`)
    REFERENCES `dojo_tweets_db`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
